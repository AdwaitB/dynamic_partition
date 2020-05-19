import concurrent.futures
import os
import time

import pandas as pd
import requests
from LRU import LRUCache
from flask import Flask, request, send_file
from flask_restful import Api
from infra_parser import *
from routing_db import *
from utils import *

logging.basicConfig(level=logging.DEBUG)

from werkzeug.serving import WSGIRequestHandler

WSGIRequestHandler.protocol_version = "HTTP/1.1"
app = Flask(__name__)
api = Api(app)
table = Table()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=N_THREADS)
my_cache = LRUCache(MAX_CACHE_SIZE)

entries = {
	Entries.INSERT_ENTRIES.name: [],
	Entries.ADD_ENTRIES.name: [],
	Entries.REMOVE_ENTRIES.name: [],
	Entries.DELETE_ENTRIES.name: [],
	Entries.CONTROL_ENTRIES.name: []
}

if not do_async:
	logging.debug("Requests are blocking")


@app.route('/', methods=['POST'])
def handler():
	request_json = request.get_json()

	output = 0

	logging.debug("{}:DEFAULT:{}".format(dt.now(), request_json))

	global executor

	if request_json[TYPE] == RequestType.DHT.name:
		output = handle_dht(request_json)
	if request_json[TYPE] == RequestType.INSERT.name:
		executor.submit(handle_insert, request_json)
		return json.dumps({"output": str(output), "request_json": request_json}) + "\n\n"
	elif request_json[TYPE] == RequestType.ADD.name:
		executor.submit(handle_add, request_json)
		return json.dumps({"output": str(output), "request_json": request_json}) + "\n\n"
	elif request_json[TYPE] == RequestType.REMOVE.name:
		executor.submit(handle_remove, request_json)
		return json.dumps({"output": str(output), "request_json": request_json}) + "\n\n"
	elif request_json[TYPE] == RequestType.DELETE.name:
		executor.submit(handle_del, request_json)
		return json.dumps({"output": str(output), "request_json": request_json}) + "\n\n"
	elif request_json[TYPE] == RequestType.CONTROL.name:
		output = handle_control(request_json)
	elif request_json[TYPE] == RequestType.DOWNLOAD.name:
		logging.debug("{}:HANDLE DOWNLOAD:START".format(dt.now()))
		if os.path.exists(FILE_FOLDER + str(request_json[FH])):
			return send_file(FILE_FOLDER + str(request_json[FH]), as_attachment=True)
		elif os.path.exists(FILE_CACHE + str(request_json[FH])):
			return send_file(FILE_CACHE + str(request_json[FH]), as_attachment=True)
		else:
			logging.debug("{} - FILE NOT FOUND : ".format(dt.now(), str(request_json[FH])))
			return json.dumps({"output": "404", "request_json": request_json}) + "\n\n"

	elif request_json[TYPE] == RequestType.JOB.name:
		output = handle_job(request_json)

	return json.dumps({"output": output, "request_json": request_json}) + "\n\n"


def handle_dht(request_json):
	"""
	If subtype is request, Handles the DHT request for a file hash.
	If the subtype is ack, Updated the list of source ips of the requesting node
	:param request_json: The file hash and the ip of the requesting node
	:return: set of nodes which have the ip
	"""

	if request_json[SUBTYPE] == 'request':
		return table.dht_ips[str(request_json[FH])]
	elif request_json[SUBTYPE] == 'ack':
		table.dht_ips[str(request_json[FH])].append(request_json[FSIP])
		return "OK"
	elif request_json[SUBTYPE] == 'del':
		if request_json[FSIP] in table.dht_ips[str(request_json[FH])]:
			table.dht_ips[str(request_json[FH])].remove(request_json[FSIP])
			return "OK"


def handle_insert(request_json):
	"""
	Handles an INSERT Request. Inserts a new replica into the current node
	:param request_json: json of the post method
	:return: send_json that was sent to the peers, spt_children
	"""
	request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

	logging.debug("{}:HANDLE INSERT:START".format(dt.now()))

	if request_json[FSIP] == table.my_ip:
		logging.debug("{}:HANDLE INSERT:END SHORT".format(dt.now()))
		return {"send_json": "{}", "children": []}

	spt_children, clock = table.handle_insert(
		(request_json[FH], request_json[FSIP])
	)

	send_json = deepcopy(request_json)
	send_json[TYPE] = RequestType.ADD.name
	send_json[RequestAdd.entry_ip.name] = table.my_ip
	send_json[RequestAdd.entry_clock.name] = clock

	executor = None
	if do_async and len(spt_children) > 0:
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(spt_children))
	for neighbour in spt_children:
		if do_async:
			executor.submit(load_url, generate_url(neighbour), send_json)
		else:
			my_session.post(generate_url(neighbour), json=send_json, timeout=HTTP_TIMEOUT)

	entries[Entries.INSERT_ENTRIES.name].append({
		TS: str(dt.now()),
		"neighbours": spt_children,
		"request_json": request_json,
		"send_json": send_json
	})

	logging.debug("{}:HANDLE INSERT:END".format(dt.now()))

	return {"send_json": send_json, "children": spt_children}


def handle_add(request_json):
	"""
	Handles an ADD request. Updates the entries for the file in current node.
	If this is better, then it also propogates the message to the nodes along the SPT.
	:param request_json: json of the post method
	:return: spt_children
	"""
	request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

	logging.debug("{}:HANDLE ADD:START".format(dt.now()))

	spt_children = table.handle_add(
		(request_json[FH], request_json[FSIP]),
		(request_json[RequestAdd.entry_ip.name], request_json[RequestAdd.entry_clock.name])
	)

	executor = None
	if do_async and len(spt_children) > 0:
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(spt_children))
	for neighbour in spt_children:
		logging.debug("{}:HANDLE ADD:ADD Send {}:{}".format(dt.now(), neighbour, request_json))
		if do_async:
			executor.submit(load_url, generate_url(neighbour), request_json)
		else:
			my_session.post(generate_url(neighbour), json=request_json, timeout=HTTP_TIMEOUT)

	entries[Entries.ADD_ENTRIES.name].append({
		TS: str(dt.now()),
		"request_json": request_json,
		"neighbours": spt_children
	})

	logging.debug("{}:HANDLE ADD:END".format(dt.now()))

	return {"children": spt_children}


def handle_remove(request_json):
	"""
	Handles an REMOVE request. Removes the entry for this node from the table and then broadcasts
	:param request_json: json of the post method
	:return: old_best_entry, new_best_entry, neighbours
	"""
	request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

	logging.debug("{}:HANDLE REMOVE:START".format(dt.now()))

	old_best_entry, new_best_entry, neighbours = table.handle_remove(
		(request_json[FH], request_json[FSIP])
	)

	send_json = deepcopy(request_json)
	send_json[TYPE] = RequestType.DELETE.name
	send_json[RequestDel.remove_src_ip.name] = old_best_entry[0]
	send_json[RequestDel.remove_src_clock.name] = old_best_entry[1]
	send_json[RequestDel.sender_ip.name] = table.my_ip
	send_json[RequestDel.sender_entry_ip.name] = new_best_entry[0]
	send_json[RequestDel.sender_entry_clock.name] = new_best_entry[1]

	executor = None
	if do_async and len(neighbours) > 0:
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(neighbours))
	for neighbour in neighbours:
		logging.debug("{}:HANDLE REMOVE:SEND {}:{}".format(dt.now(), neighbour, send_json))
		if do_async:
			executor.submit(load_url, generate_url(neighbour), send_json)
		else:
			my_session.post(generate_url(neighbour), json=send_json, timeout=HTTP_TIMEOUT)

	entries[Entries.REMOVE_ENTRIES.name].append({
		TS: str(dt.now()),
		"request_json": request_json,
		"send_json": send_json,
		"neighbours": neighbours
	})

	logging.debug("{}:HANDLE REMOVE:END".format(dt.now()))

	return {"old_best": old_best_entry, "new_best": new_best_entry, "neighbours": neighbours}


def handle_del(request_json):
	"""
	Handles a del message.
	:param request_json: json of the post method
	:return: the add and del tasks
	"""
	request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

	logging.debug("{}:HANDLE DEL:START".format(dt.now()))

	tasks = table.handle_del(
		(request_json[FH], request_json[FSIP]),
		(request_json[RequestDel.remove_src_ip.name], request_json[RequestDel.remove_src_clock.name]),
		request_json[RequestDel.sender_ip.name],
		(request_json[RequestDel.sender_entry_ip.name], request_json[RequestDel.sender_entry_clock.name])
	)

	total = 0
	if tasks[RequestType.DELETE.name]:
		total += len(tasks[RequestType.DELETE.name]["neighbours"])
	if tasks[RequestType.ADD.name]:
		total += 1

	executor = None
	if do_async and total > 0:
		executor = concurrent.futures.ThreadPoolExecutor(max_workers=total)

	if tasks[RequestType.DELETE.name]:
		send_json = {
			TYPE: RequestType.DELETE.name,
			FH: request_json[FH],
			FSIP: request_json[FSIP],
			RequestDel.remove_src_ip.name: request_json[RequestDel.remove_src_ip.name],
			RequestDel.remove_src_clock.name: request_json[RequestDel.remove_src_clock.name],
			RequestDel.sender_ip.name: table.my_ip,
			RequestDel.sender_entry_ip.name: tasks[RequestType.DELETE.name]["new_best"][0],
			RequestDel.sender_entry_clock.name: tasks[RequestType.DELETE.name]["new_best"][1]
		}

		for neighbour in tasks[RequestType.DELETE.name]["neighbours"]:
			logging.debug("{}:HANDLE DEL:DEL SEND {}:{}".format(dt.now(), neighbour, send_json))
			if do_async:
				executor.submit(load_url, generate_url(neighbour), send_json)
			else:
				my_session.post(generate_url(neighbour), json=send_json, timeout=HTTP_TIMEOUT)

	if tasks[RequestType.ADD.name]:
		send_json = {
			TYPE: RequestType.ADD.name,
			FH: request_json[FH],
			FSIP: request_json[FSIP],
			RequestAdd.entry_ip.name: tasks[RequestType.ADD.name]["new_best"][0],
			RequestAdd.entry_clock.name: tasks[RequestType.ADD.name]["new_best"][1]
		}

		logging.debug("{}:HANDLE DEL:ADD SEND {}:{}".format(dt.now(), tasks[RequestType.ADD.name]["ip"], send_json))
		if do_async:
			executor.submit(load_url, generate_url(tasks[RequestType.ADD.name]["ip"]), send_json)
		else:
			my_session.post(generate_url(tasks[RequestType.ADD.name]["ip"]), json=send_json, timeout=HTTP_TIMEOUT)

	entries[Entries.DELETE_ENTRIES.name].append({
		TS: str(dt.now()),
		"request_json": request_json,
		"tasks": tasks
	})

	logging.debug("{}:HANDLE DEL:END".format(dt.now()))

	return {"tasks": tasks}


def handle_control(request_json):
	if request_json[SUBTYPE] == RequestSubtype.INIT.name:
		logging.debug("{}: CONTROL INIT: START".format(dt.now()))

		# IP of self
		table.update_my_ip(request_json["ip"])

		# mapping for files and source
		table.src_ips = request_json["mapping"]

		table.node_mapping = request_json['node_mapping']

		# Get the fh corresponding to self
		table.generate_dht_src()

		logging.debug("{}: CONTROL INIT: DHT SRC {}".format(
			dt.now(), table.dht_ips
		))

		entries[Entries.CONTROL_ENTRIES.name].append(request_json)

		logging.debug("{}: CONTROL INIT: END".format(dt.now()))
		return 0
	elif request_json[SUBTYPE] == RequestSubtype.FILE.name:
		os.rename(FILE_FOLDER + str(request_json['File Size']), FILE_FOLDER + str(request_json[FH]))
		logging.debug("{}:HANDLE CONTROL:FILE HASH, hash : {}".format(dt.now(), request_json['file_hash']))
		return 0
	elif request_json[SUBTYPE] == RequestSubtype.WRITE_TRACE.name:
		# Generate CSV traces
		for trace_type in entries:
			data = pd.DataFrame(entries[trace_type])
			data.to_csv(TRACES_FOLDER + trace_type + ".csv")

		# Generate json traces
		entries['node_ip'] = table.my_ip
		entries['table'] = table.get_snapshot()

		with open(TRACES_FOLDER + 'traces.json', 'w') as json_file:
			json.dump(entries, json_file)

		return 0


def handle_job(request_json):
	logging.debug("{}:HANDLE JOB:START".format(dt.now()))

	# First check if file exists
	if os.path.exists(FILE_FOLDER + str(request_json[FH])) or os.path.exists(FILE_CACHE + str(request_json[FH])):
		return {"time_download": 0, "req_time": 0, "ignore": 1}

	if request_json['iter'] == "new":
		req_time, download_time, ip = do_new_query(request_json)
	else:
		req_time, download_time, ip = do_dht_query(request_json)

	logging.debug("{}:HANDLE JOB:END".format(dt.now()))

	return {"time_download": download_time, "req_time": req_time, "ignore": 0}


def do_new_query(request_json):
	logging.debug("{}:HANDLE JOB:NEW START".format(dt.now()))
	fhash = request_json[FH]

	time_init = time.time()

	ip = table.get_best_entry_for_file(
		(request_json[FH], table.src_ips[str(request_json[FH])]['source'])
	)
	ip = ip[0]

	req_time = time.time() - time_init

	download_time, removed_hash = do_download(request_json[FH], ip)

	download_time_with_file_write = time.time() - req_time - time_init

	logging.debug("{}:HANDLE JOB:NEW, ip : {}".format(dt.now(), ip))

	# Do an insert
	insert_json = {
		TYPE: RequestType.INSERT.name,
		FH: fhash,
		RequestAdd.add_id.name: request_json[RequestAdd.add_id.name]
	}
	my_session.post(generate_url(), json=insert_json, timeout=HTTP_TIMEOUT)

	# Trigger a DEL message if removed_hash != 0
	if removed_hash != 0:
		remove_json = {
			TYPE: RequestType.REMOVE.name,
			FH: removed_hash,
		}
		my_session.post(generate_url(), json=remove_json, timeout=HTTP_TIMEOUT)
		logging.debug("{}:TRIGGER REMOVE: {}".format(dt.now(), removed_hash))

	logging.debug("{}:HANDLE JOB:NEW END, time = {}".format(dt.now(), time_init))
	return req_time, download_time, ip


def do_dht_query(request_json):
	logging.debug("{}:HANDLE JOB:DHT START".format(dt.now()))
	fhash = int(request_json[FH])

	time_init = time.time()

	dht_ip = table.get_ip_by_value(fhash % table.n)

	dht_json = {
		TYPE: RequestType.DHT.name,
		SUBTYPE: 'request',
		FH: fhash
	}

	ips = my_session.post(generate_url(dht_ip), json=dht_json, timeout=HTTP_TIMEOUT)
	ips = json.loads(ips.text)['output']

	nearest_ip = ips[0]
	nearest_dist = table.infra.shortest_path_dist[nearest_ip][table.my_ip]

	for ip in ips:
		if table.infra.shortest_path_dist[ip][table.my_ip] < nearest_dist:
			nearest_ip = ip
			nearest_dist = table.infra.shortest_path_dist[ip][table.my_ip]

	req_time = time.time() - time_init

	download_time, removed_hash = do_download(request_json[FH], nearest_ip)

	download_time_with_file_write = time.time() - req_time - time_init

	logging.debug("{}:HANDLE JOB:DHT, nearest source : {}, all sources : {}".format(dt.now(), nearest_ip, ips))
	logging.debug("{}:DEBUG:DHT, req_time: {}, latency: {}, my_ip: {}, dht_ip: {}".format(dt.now(), req_time,
																						  table.infra.shortest_path_dist[
																							  dht_ip][table.my_ip],
																						  table.my_ip, dht_ip))

	# Do an ack
	send_json_ack = {
		TYPE: RequestType.DHT.name,
		SUBTYPE: 'ack',
		FH: fhash,
		FSIP: table.my_ip
	}
	my_session.post(generate_url(dht_ip), json=send_json_ack, timeout=HTTP_TIMEOUT)

	# Trigger a DEL message if removed_hash != 0
	if removed_hash != 0:
		send_json_del = {
			TYPE: RequestType.DHT.name,
			SUBTYPE: 'del',
			FH: removed_hash,
			FSIP: table.my_ip
		}
		dht_ip_remove = table.get_ip_by_value(removed_hash % table.n)
		logging.debug(
			"{}:TRIGGER REMOVE: , file_hash = {}, my_ip = {}, dht_ip = {}".format(dt.now(), removed_hash, table.my_ip,
																				  dht_ip_remove))
		my_session.post(generate_url(dht_ip_remove), json=send_json_del, timeout=HTTP_TIMEOUT)

	logging.debug("{}:HANDLE JOB:DHT END, time = {}".format(dt.now(), time_init))

	return req_time, download_time, nearest_ip


def do_download(fhash, ip):
	time_download = time.time()

	send_json = {
		TYPE: RequestType.DOWNLOAD.name,
		FH: fhash
	}

	file_data = my_session.post(generate_url(ip), json=send_json, timeout=HTTP_TIMEOUT)
	logging.debug(
		"{}: Download file from: {} - {} - {}".format(dt.now(), fhash, ip, table.src_ips[str(fhash)]['source']))

	time_download = time.time() - time_download

	global my_cache
	removed_hash = my_cache.set(fhash, len(file_data.text))
	logging.debug("{}:CONTENT OF MY CACHE = {}".format(dt.now(), my_cache.cache))

	# Write the file
	with open(FILE_CACHE + str(fhash), "w") as text_file:
		text_file.write(file_data.text)

	# Delete the removed file from cache space
	if removed_hash != 0 and os.path.exists(FILE_CACHE + str(removed_hash)):
		os.remove(FILE_CACHE + str(removed_hash))

	return time_download, removed_hash


if __name__ == '__main__':
	my_session = requests.Session()
	from requests.adapters import HTTPAdapter

	my_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=100))
	app.run(port=NODE_CUSTOM_PORT, host='0.0.0.0')
