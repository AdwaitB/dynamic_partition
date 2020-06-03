import concurrent.futures
import os
import time
import pandas as pd
from flask import Flask, request, send_file
from flask_restful import Api
from LRU import LRUCache
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
ongoing_downloads = set()
atomic = {}

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

    logging.debug("{}:JOB ID {}:DEFAULT:{}".format(dt.now(), request_json['job_id'], request_json))

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
        logging.debug("{}:JOB ID {}:HANDLE DOWNLOAD:START:".format(dt.now(), request_json['job_id']))
        if os.path.exists(FILE_FOLDER + str(request_json[FH])):
            logging.debug(
                "{}:JOB ID {}:HANDLE DOWNLOAD:OWNER:{}".format(dt.now(), request_json['job_id'], str(request_json[FH])))
            return send_file(FILE_FOLDER + str(request_json[FH]), as_attachment=True)
        elif os.path.exists(FILE_CACHE + str(request_json[FH])):
            logging.debug(
                "{}:JOB ID {}:HANDLE DOWNLOAD:CACHE:{}".format(dt.now(), request_json['job_id'], str(request_json[FH])))
            return send_file(FILE_CACHE + str(request_json[FH]), as_attachment=True)
        else:
            logging.debug(
                "{}:JOB ID {}:FILE NOT FOUND:{}".format(dt.now(), request_json['job_id'], str(request_json[FH])))
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
    logging.debug("{}:JOB ID {}:HANDLE DHT:START:".format(dt.now(), request_json['job_id']))

    if request_json[SUBTYPE] == 'request':
        logging.debug("{}:JOB ID {}:HANDLE DHT:REQUEST:{}".format(dt.now(), request_json['job_id'],
                                                                  table.dht_ips[str(request_json[FH])]))
        return table.dht_ips[str(request_json[FH])]
    elif request_json[SUBTYPE] == 'ack':
        logging.debug("{}:JOB ID {}:HANDLE DHT:ACK:".format(dt.now(), request_json['job_id']))
        if request_json[FSIP] not in table.dht_ips[str(request_json[FH])]:
            table.dht_ips[str(request_json[FH])].append(request_json[FSIP])
        return "OK"
    elif request_json[SUBTYPE] == 'del':
        logging.debug("{}:JOB ID {}:HANDLE DHT:DEL:".format(dt.now(), request_json['job_id']))
        if request_json[FSIP] in table.dht_ips[str(request_json[FH])]:
            table.dht_ips[str(request_json[FH])].remove(request_json[FSIP])
            return "OK"


def handle_insert(request_json):
    """
    Handles an INSERT Request. Inserts a new replica into the current node
    :param request_json: json of the post method
    :return: send_json that was sent to the peers, spt_children
    """
    get_lock_for_hash(request_json[FH])  # Ensure atomicity
    logging.debug("{}:JOB ID {}:HANDLE INSERT:START:".format(dt.now(), request_json['job_id']))

    request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

    if request_json[FSIP] == table.my_ip:
        logging.debug("{}:JOB ID {}:HANDLE INSERT:END SHORT:".format(dt.now(), request_json['job_id']))
        return {"send_json": {}, "children": []}

    logging.debug("{}:JOB ID {}:Before calling routing Insert".format(dt.now(), request_json['job_id']))
    spt_children, clock = table.handle_insert(
        (request_json[FH], request_json[FSIP]), request_json['job_id']
    )
    logging.debug("{}:JOB ID {}:After calling routing Insert".format(dt.now(), request_json['job_id']))

    send_json = deepcopy(request_json)
    send_json[TYPE] = RequestType.ADD.name
    send_json[RequestAdd.entry_ip.name] = table.my_ip
    send_json[RequestAdd.entry_clock.name] = clock
    send_json['job_id'] = request_json['job_id']

    logging.debug("{}:JOB ID {}:HANDLE INSERT:SEND TO CHILDREN: {}:".format(dt.now(), request_json['job_id'], spt_children))
    for neighbour in spt_children:
        if do_async:
            executor.submit(load_url, generate_url(neighbour), send_json)
        else:
            logging.debug("{}:JOB ID {}:HANDLE INSERT:SEND TO {}:".format(dt.now(), request_json['job_id'], generate_url(neighbour)))
            my_session.post(generate_url(neighbour), json=send_json, timeout=HTTP_TIMEOUT)

    entries[Entries.INSERT_ENTRIES.name].append({
        TS: str(dt.now()),
        "neighbours": spt_children,
        "request_json": request_json,
        "send_json": send_json,
        "job_id": request_json['job_id']
    })

    logging.debug("{}:JOB ID {}:HANDLE INSERT:END:".format(dt.now(), request_json['job_id']))

    release_lock_for_hash(request_json[FH])  # Ensure atomicity
    return {"send_json": send_json, "children": spt_children}


def handle_add(request_json):
    """
    Handles an ADD request. Updates the entries for the file in current node.
    If this is better, then it also propogates the message to the nodes along the SPT.
    :param request_json: json of the post method
    :return: spt_children
    """
    get_lock_for_hash(request_json[FH])  # Ensure atomicity
    logging.debug("{}:JOB ID {}:HANDLE ADD:START:".format(dt.now(), request_json['job_id']))

    request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

    spt_children = table.handle_add(
        (request_json[FH], request_json[FSIP]),
        (request_json[RequestAdd.entry_ip.name], request_json[RequestAdd.entry_clock.name]), 
        request_json['job_id']
    )

    for neighbour in spt_children:
        logging.debug(
            "{}:JOB ID {}:HANDLE ADD:NEIGHBOURS:neighbours = {}".format(dt.now(), request_json['job_id'], neighbour))
        if do_async:
            executor.submit(load_url, generate_url(neighbour), request_json)
        else:
            my_session.post(generate_url(neighbour), json=request_json, timeout=HTTP_TIMEOUT)

    entries[Entries.ADD_ENTRIES.name].append({
        TS: str(dt.now()),
        "request_json": request_json,
        "neighbours": spt_children,
        "job_id": request_json['job_id']
    })

    logging.debug("{}:JOB ID {}:HANDLE ADD:END:".format(dt.now(), request_json['job_id']))
    release_lock_for_hash(request_json[FH])  # Ensure atomicity
    return {"children": spt_children}


def handle_remove(request_json):
    """
    Handles an REMOVE request. Removes the entry for this node from the table and then broadcasts
    :param request_json: json of the post method
    :return: old_best_entry, new_best_entry, neighbours
    """
    get_lock_for_hash(request_json[FH])  # Ensure atomicity
    logging.debug("{}:JOB ID {}:HANDLE REMOVE:START:".format(dt.now(), request_json['job_id']))

    request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

    old_best_entry, new_best_entry, neighbours = table.handle_remove(
        (request_json[FH], request_json[FSIP]), request_json['job_id']
    )

    send_json = deepcopy(request_json)
    send_json[TYPE] = RequestType.DELETE.name
    send_json[RequestDel.remove_src_ip.name] = old_best_entry[0]
    send_json[RequestDel.remove_src_clock.name] = old_best_entry[1]
    send_json[RequestDel.sender_ip.name] = table.my_ip
    send_json[RequestDel.sender_entry_ip.name] = new_best_entry[0]
    send_json[RequestDel.sender_entry_clock.name] = new_best_entry[1]
    send_json['job_id'] = request_json['job_id']

    for neighbour in neighbours:
        logging.debug("{}:JOB ID {}:HANDLE REMOVE:NEIGHBOURS:neighbours = {}, send_json = {}".format(
            dt.now(), request_json['job_id'], neighbour, send_json)
        )

        if do_async:
            executor.submit(load_url, generate_url(neighbour), send_json)
        else:
            my_session.post(generate_url(neighbour), json=send_json, timeout=HTTP_TIMEOUT)

    entries[Entries.REMOVE_ENTRIES.name].append({
        TS: str(dt.now()),
        "request_json": request_json,
        "send_json": send_json,
        "neighbours": neighbours,
        "job_id": request_json['job_id']
    })

    logging.debug("{}:JOB ID {}:HANDLE REMOVE:END:".format(dt.now(), request_json['job_id']))
    release_lock_for_hash(request_json[FH])  # Ensure atomicity
    return {"old_best": old_best_entry, "new_best": new_best_entry, "neighbours": neighbours}


def handle_del(request_json):
    """
    Handles a del message.
    :param request_json: json of the post method
    :return: the add and del tasks
    """
    get_lock_for_hash(request_json[FH])  # Ensure atomicity
    logging.debug("{}:JOB ID {}:HANDLE DEL:START:".format(dt.now(), request_json['job_id']))

    request_json[FSIP] = table.src_ips[str(request_json[FH])]['source']

    tasks = table.handle_del(
        (request_json[FH], request_json[FSIP]),
        (request_json[RequestDel.remove_src_ip.name], request_json[RequestDel.remove_src_clock.name]),
        request_json[RequestDel.sender_ip.name],
        (request_json[RequestDel.sender_entry_ip.name], request_json[RequestDel.sender_entry_clock.name]),
        request_json['job_id']
    )

    total = 0
    if tasks[RequestType.DELETE.name]:
        total += len(tasks[RequestType.DELETE.name]["neighbours"])
    if tasks[RequestType.ADD.name]:
        total += 1

    if tasks[RequestType.DELETE.name]:
        send_json = {
            TYPE: RequestType.DELETE.name,
            FH: request_json[FH],
            FSIP: request_json[FSIP],
            RequestDel.remove_src_ip.name: request_json[RequestDel.remove_src_ip.name],
            RequestDel.remove_src_clock.name: request_json[RequestDel.remove_src_clock.name],
            RequestDel.sender_ip.name: table.my_ip,
            RequestDel.sender_entry_ip.name: tasks[RequestType.DELETE.name]["new_best"][0],
            RequestDel.sender_entry_clock.name: tasks[RequestType.DELETE.name]["new_best"][1],
            'job_id': request_json['job_id']
        }

        for neighbour in tasks[RequestType.DELETE.name]["neighbours"]:
            logging.debug("{}:JOB ID {}:HANDLE DEL:NEIGHBOURS:{}:{}".format(dt.now(), request_json['job_id'], neighbour,
                                                                            send_json))
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
            RequestAdd.entry_clock.name: tasks[RequestType.ADD.name]["new_best"][1],
            'job_id': request_json['job_id']
        }

        logging.debug("{}:JOB ID {}:HANDLE DEL:ADD SEND:{}:{}".format(dt.now(), request_json['job_id'],
                                                                      tasks[RequestType.ADD.name]["ip"], send_json))
        if do_async:
            executor.submit(load_url, generate_url(tasks[RequestType.ADD.name]["ip"]), send_json)
        else:
            my_session.post(generate_url(tasks[RequestType.ADD.name]["ip"]), json=send_json, timeout=HTTP_TIMEOUT)

    entries[Entries.DELETE_ENTRIES.name].append({
        TS: str(dt.now()),
        "request_json": request_json,
        "tasks": tasks,
        "job_id": request_json['job_id']
    })

    logging.debug("{}:JOB ID {}:HANDLE DEL:END:".format(dt.now(), request_json['job_id']))
    release_lock_for_hash(request_json[FH])  # Ensure atomicity
    return {"tasks": tasks}


def handle_control(request_json):
    if request_json[SUBTYPE] == RequestSubtype.INIT.name:
        logging.debug("{}:JOB ID {}:HANDLE CONTROL:INIT:START:".format(dt.now(), request_json['job_id']))

        # IP of self
        table.update_my_ip(request_json["ip"])

        # mapping for files and source
        table.src_ips = request_json["mapping"]

        table.node_mapping = request_json['node_mapping']

        # Get the fh corresponding to self
        table.generate_dht_src()

        logging.debug("{}:JOB ID {}:HANDLE CONTROL:INIT:dht_source = {}".format(
            dt.now(), request_json['job_id'], table.dht_ips
        ))

        entries[Entries.CONTROL_ENTRIES.name].append(request_json)

        logging.debug("{}:JOB ID {}:HANDLE CONTROLINIT::END:".format(dt.now(), request_json['job_id']))
        return 0
    elif request_json[SUBTYPE] == RequestSubtype.FILE.name:
        os.rename(FILE_FOLDER + str(request_json['File Size']), FILE_FOLDER + str(request_json[FH]))
        logging.debug("{}:JOB ID {}:HANDLE CONTROL:FILE:hash = {}".format(dt.now(), request_json['job_id'],
                                                                          request_json['file_hash']))
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
    elif request_json[SUBTYPE] == RequestSubtype.FINALIZE.name:
        executor.shutdown(wait=True)
        return 0

    return 0


def handle_job(request_json):
    global ongoing_downloads
    logging.debug("{}:JOB ID {}:HANDLE JOB:START:".format(dt.now(), request_json['job_id']))

    # First check if file exists
    if os.path.exists(FILE_FOLDER + str(request_json[FH])) or os.path.exists(FILE_CACHE + str(request_json[FH])):
        return {"time_download": 0, "req_time": 0, "ignore": 1}

    # Check if download is not already ongoing
    if request_json[FH] in ongoing_downloads:
        logging.debug("{}:JOB ID {}:Download already ongoing:".format(dt.now(), request_json['job_id']))
        return {"time_download": 0, "req_time": 0, "ignore": 1}

    ongoing_downloads.add(request_json[FH])

    if request_json['iter'].startswith("new"):
        req_time, download_time, ip = do_new_query(request_json)
    elif request_json['iter'].startswith("dht"):
        req_time, download_time, ip = do_dht_query(request_json)
    elif request_json['iter'] == "baseline":
        download_time, removed_hash = do_download(request_json[FH], table.src_ips[str(request_json[FH])]['source'], request_json)
        req_time = 0

    logging.debug("{}:JOB ID {}:HANDLE JOB:END:".format(dt.now(), request_json['job_id']))

    ongoing_downloads.discard(request_json[FH])

    return {"time_download": download_time, "req_time": req_time, "ignore": 0}


def do_new_query(request_json):
    logging.debug("{}:JOB ID {}:HANDLE JOB:NEW START:".format(dt.now(), request_json['job_id']))

    fhash = request_json[FH]

    time_init = time.time()

    ip = table.get_best_entry_for_file(
        (request_json[FH], table.src_ips[str(request_json[FH])]['source'])
    )
    ip = ip[0]

    req_time = time.time() - time_init

    download_time, removed_hash = do_download(request_json[FH], ip, request_json)

    download_time_with_file_write = time.time() - req_time - time_init

    logging.debug("{}:JOB ID {}:HANDLE JOB:NEW:best_ip = {}".format(dt.now(), request_json['job_id'], ip))

    # Do an insert
    insert_json = {
        TYPE: RequestType.INSERT.name,
        FH: fhash,
        'job_id': request_json['job_id']
    }
    my_session.post(generate_url(), json=insert_json, timeout=HTTP_TIMEOUT)

    # Trigger a DEL message if removed_hash != 0
    if removed_hash != 0:
        remove_json = {
            TYPE: RequestType.REMOVE.name,
            FH: removed_hash,
            'job_id': request_json['job_id']
        }
        my_session.post(generate_url(), json=remove_json, timeout=HTTP_TIMEOUT)
        logging.debug(
            "{}:JOB ID {}:TRIGGER REMOVE:removed_hash = {}".format(dt.now(), request_json['job_id'], removed_hash))

    logging.debug("{}:JOB ID {}:HANDLE JOB:NEW END:time = {}".format(dt.now(), request_json['job_id'], time_init))
    return req_time, download_time, ip


def do_dht_query(request_json):
    logging.debug("{}:JOB ID {}:HANDLE JOB:DHT START:".format(dt.now(), request_json['job_id']))
    fhash = int(request_json[FH])

    time_init = time.time()

    dht_ip = table.get_ip_by_value(fhash % table.n)

    dht_json = {
        TYPE: RequestType.DHT.name,
        SUBTYPE: 'request',
        FH: fhash,
        'job_id': request_json['job_id']
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

    download_time, removed_hash = do_download(request_json[FH], nearest_ip, request_json)

    download_time_with_file_write = time.time() - req_time - time_init

    logging.debug(
        "{}:JOB ID {}:HANDLE JOB:DHT:nearest source : {}, all sources: {}".format(dt.now(), request_json['job_id'],
                                                                                  nearest_ip, ips))
    logging.debug("{}:JOB ID {}:DEBUG:DHT:req_time: {}, latency: {}, my_ip: {}, dht_ip: {}".format(dt.now(),
                                                                                                   request_json[
                                                                                                       'job_id'],
                                                                                                   req_time,
                                                                                                   table.infra.shortest_path_dist[
                                                                                                       dht_ip][
                                                                                                       table.my_ip],
                                                                                                   table.my_ip, dht_ip))

    # Do an ack
    send_json_ack = {
        TYPE: RequestType.DHT.name,
        SUBTYPE: 'ack',
        FH: fhash,
        FSIP: table.my_ip,
        'job_id': request_json['job_id']
    }
    my_session.post(generate_url(dht_ip), json=send_json_ack, timeout=HTTP_TIMEOUT)

    # Trigger a DEL message if removed_hash != 0
    if removed_hash != 0:
        send_json_del = {
            TYPE: RequestType.DHT.name,
            SUBTYPE: 'del',
            FH: removed_hash,
            FSIP: table.my_ip,
            'job_id': request_json['job_id']
        }
        dht_ip_remove = table.get_ip_by_value(removed_hash % table.n)
        logging.debug(
            "{}:JOB ID {}:TRIGGER REMOVE:file_hash = {}, my_ip = {}, dht_ip = {}".format(dt.now(),
                                                                                         request_json['job_id'],
                                                                                         removed_hash, table.my_ip,
                                                                                         dht_ip_remove))
        my_session.post(generate_url(dht_ip_remove), json=send_json_del, timeout=HTTP_TIMEOUT)

    logging.debug("{}:JOB ID {}:HANDLE JOB:DHT END:time = {}".format(dt.now(), request_json['job_id'], time_init))

    return req_time, download_time, nearest_ip


def do_download(fhash, ip, request_json):
    time_download = time.time()

    send_json = {
        TYPE: RequestType.DOWNLOAD.name,
        FH: fhash,
        'job_id': request_json['job_id']
    }

    file_data = my_session.post(generate_url(ip), json=send_json, timeout=HTTP_TIMEOUT)

    if file_data.headers.get('content-type') != "application/octet-stream": # Fallback to the source and add the time to get 404 + time to get file from the source.
        logging.debug("{}:JOB ID {}:Error 404 Fall back to source:file_hash = {}, location = {}, source_ip = {}".format(dt.now(), request_json['job_id'], fhash, ip, table.src_ips[str(fhash)]['source']))
        file_data = my_session.post(generate_url(table.src_ips[str(fhash)]['source']), json=send_json, timeout=HTTP_TIMEOUT)
        time_download = time.time() - time_download

    else: # File has been downloaded correctly
        logging.debug("{}:JOB ID {}:HANDLE JOB:DOWNLOAD:file_hash = {}, location = {}, source_ip = {}".format(dt.now(), request_json['job_id'], fhash, ip, table.src_ips[str(fhash)]['source']))
        time_download = time.time() - time_download

    global my_cache
    removed_hash = my_cache.set(fhash, len(file_data.text))
    logging.debug("{}:JOB ID {}:HANDLE JOB:DOWNLOAD:Cache = {}".format(dt.now(), request_json['job_id'], my_cache.cache))

    # Write the file
    with open(FILE_CACHE + str(fhash), "w") as text_file:
        text_file.write(file_data.text)

    # Delete the removed file from cache space
    if removed_hash != 0 and os.path.exists(FILE_CACHE + str(removed_hash)):
        os.remove(FILE_CACHE + str(removed_hash))

    return time_download, removed_hash


def get_lock_for_hash(file_id):
    global atomic
    if file_id not in atomic:
        atomic[file_id] = threading.Lock()
    atomic[file_id].acquire()

def release_lock_for_hash(file_id):
    global atomic
    if file_id not in atomic:
        logging.debug("{}:BUG: No lock entries for this file hash {}".format(dt.now(), file_id))
    atomic[file_id].release()


if __name__ == '__main__':
    my_session = requests.Session()
    from requests.adapters import HTTPAdapter

    my_session.mount('http://', HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=100))
    app.run(port=NODE_CUSTOM_PORT, host='0.0.0.0')
