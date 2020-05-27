import concurrent.futures
import random
import sched
import sys
import time
import pandas
from matplotlib import pyplot as plt
from infra_parser import *
from utils import *
from datetime import datetime as dt

logging.basicConfig(level=logging.DEBUG)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=N_THREADS)
# Wait for node services to start
time.sleep(10)
infra = Infra()


def initialize_nodes(mapping):
	print("Initialization of Nodes")

	# Post the initialization to all nodes
	ips = []
	send_json_list = []

	# Generate the node mappings
	node_mapping = {}
	node_value = 0

	for node in infra.infra:
		if node == "master":
			continue
		node_mapping[infra.get_ip_by_name(node)] = node_value
		node_value += 1

	for node in infra.infra:
		if node == "master":
			continue
		ips.append(infra.get_ip_by_name(node))

		send_json_list.append({
			TYPE: RequestType.CONTROL.name,
			"subtype": "INIT",
			"ip": infra.get_ip_by_name(node),
			"mapping": mapping,
			"node_mapping": node_mapping,
			"job_id": -1
		})

	post_multiple(ips, send_json_list, do_async)

	print("Node mapping")
	pp(node_mapping)


def generate_files():
	mapping = {}

	ips = []
	request_json_list = []

	identifier = FILE_SIZES[len(FILE_SIZES)-1] + 1  # Initialize file hashes with a hash number superior to the
	# maximum file size to avoid overriding existing files
	for i in FILE_SIZES:
		for node in infra.get_nodes():
			ips.append(infra.get_ip_by_name(node))

			identifier += 1

			request_json_list.append({
				TYPE: RequestType.CONTROL.name,
				SUBTYPE: RequestSubtype.FILE.name,
				FH: identifier,
				'File Size': i,
				"job_id": -1
			})

			mapping[identifier] = {
				'File Size': i,
				'source': infra.get_ip_by_name(node)
			}

	post_multiple(ips, request_json_list, do_async)
	pp(mapping)
	return mapping


def do_jobs(n_jobs, mapping, step, upper, iteration_):
	print("Starting jobs")

	ips = infra.get_n_random_nodes(n_jobs)

	np.random.seed(SEED)
	datasets = np.random.choice(list(mapping.keys()), n_jobs, replace=True)

	logging.debug("{}:JOBS:ips = {}".format(dt.now(), ips))
	logging.debug("{}:JOBS:datasets = {}".format(dt.now(), datasets))
	logging.debug("{}:JOBS:mapping.keys type = {}".format(dt.now(), type(list(mapping.keys())[0])))

	random.seed(SEED)

	s = sched.scheduler(time.time, time.sleep)

	# Stores the cumulative time
	time_track = 0
	for i in range(n_jobs):
		time_track += random.uniform(0, float(upper) / 1000) + float(step) / 1000
		s.enter(time_track, 1, executor.submit, argument=(request_job, ips[i], datasets[i], i, iteration_))

	s.run()

	executor.shutdown(wait=True)

	traces = pandas.DataFrame()
	for trace in traces_list:
		traces = traces.append(trace, ignore_index=True)

	traces.to_csv(TRACES_FOLDER + "traces_{}.csv".format(iteration_))

	fig = traces.boxplot(column=['Total Time'], by='Size (B)', rot=45)
	plt.xlabel("Size of Dataset (KB)")
	plt.ylabel("Time to Download (s)")
	plt.title("Boxplot for Download time for {}".format(iteration))
	plt.savefig(TRACES_FOLDER + "traces_{}.png".format(iteration_))


def request_job(ip, dataset, job_id, iteration_):
	logging.debug("{}:JOB ID {}:START:ip = {}, dataset = {},{}".format(
		dt.now(), job_id, ip, type(dataset), dataset
	))

	send_time = dt.now()

	send_json = {
		TYPE: RequestType.JOB.name,
		FH: dataset.item(),
		"iter": iteration_,
		'job_id': job_id
	}

	logging.debug("{}:JOB ID {}:SUBMIT {}, send_json : {}, url : {}".format(
		dt.now(), job_id, time.time(), send_json, generate_url(ip)
	))

	out = requests.post(generate_url(ip), json=send_json, timeout=HTTP_TIMEOUT)

	logging.debug("{}:JOB ID {}:DEBUG {}".format(
		dt.now(), job_id, out.text
	))

	try:
		out = json.loads(out.text)
	except:
		return

	logging.debug("{}:JOB ID {}:SUBMIT COMPLETE {}".format(dt.now(), job_id, time.time()))

	entry = {
		"Job ID": job_id,
		"Identifier": dataset,
		"IP of Task": ip,
		"Time Download": out['output']['time_download'],
		"Time Request": out['output']['req_time'],
		"Total Time": out['output']['time_download'] + out['output']['req_time'],
		"Size (B)": files_mapping[dataset]['File Size'] * 4.096,
		"Post Time": send_time,
		"Return Time": dt.now()
	}

	if out['output']['ignore'] == 0:
		traces_list.append(entry)
	return


def finalize_nodes():
	print("Finalize of Nodes")
	ips = []
	send_json_list = []

	for node in infra.infra:
		if node == "master":
			continue

	for node in infra.infra:
		if node == "master":
			continue
		ips.append(infra.get_ip_by_name(node))

		send_json_list.append({
			TYPE: RequestType.CONTROL.name,
			SUBTYPE: RequestSubtype.WRITE_TRACE.name,
			"job_id": -1
		})

		finalize_json = {
			TYPE: RequestType.CONTROL.name,
			SUBTYPE: RequestSubtype.FINALIZE.name,
			"job_id": -1
		}

		requests.post(generate_url(infra.get_ip_by_name(node)), json=finalize_json, timeout=HTTP_TIMEOUT)

	post_multiple(ips, send_json_list, do_async)


iteration = sys.argv[1]

traces_list = []

files_mapping = generate_files()
initialize_nodes(files_mapping)
do_jobs(N_JOBS, files_mapping, JOB_GENERATION_A, JOB_GENERATION_B, iteration)
finalize_nodes()

print("Master Tasks Completed")
