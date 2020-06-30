import os
import json
from cons import path, get_jobID_set

# path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_5s/Renater20000Jobs_Cache20_40_60_seed777_5s/transient"
# Get nbr of messages of AAA algo:
os.chdir(path)
dict_of_download_sources = {}
results = {}
already_done = set()
jobID_set = get_jobID_set()
for filename in os.listdir(os.getcwd()):
    print(filename)
    if not filename.startswith('.'):
        if os.path.isdir(filename):
            if filename.startswith("new") or filename.startswith("dht"): cache_size = filename.split("-")[1]
            if cache_size not in already_done:
                if filename.startswith("new") or filename.startswith("dht"):
                    os.chdir(path + "/" + filename + "/")
                    if filename not in dict_of_download_sources: dict_of_download_sources.update({filename: {}})
                    for node in os.listdir(os.getcwd()):
                        os.chdir(path + "/" + filename + "/" + node + "/root/deploy/traces")
                        if os.path.exists("_node_stderr.txt"):
                            cmd = """ grep "HANDLE JOB:DOWNLOAD:file_hash" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            downloaded_files = []
                            for entry in sources_splitted:
                                first_split = entry.split(':')
                                job_id = first_split[5].split(" ")[2]
                                if job_id in jobID_set:
                                    if job_id not in dict_of_download_sources[filename]: dict_of_download_sources[
                                        filename].update({job_id: {}})
                                    file_hash = first_split[8].split(",")[0].split("=")[1]
                                    location = first_split[8].split(",")[1].split("=")[1]
                                    source = first_split[8].split(",")[2].split("=")[1]
                                    dict_of_download_sources[filename][job_id].update(
                                        {filename: (node, file_hash, location, source)})

                    already_done.add(filename.split("-")[1])
                    if "new" in filename:
                        filename = filename.replace("new", "dht")
                    elif "dht" in filename:
                        filename = filename.replace("dht", "new")
                    if filename not in dict_of_download_sources: dict_of_download_sources.update({filename: {}})
                    os.chdir(path + "/" + filename + "/")
                    for node in os.listdir(os.getcwd()):
                        os.chdir(path + "/" + filename + "/" + node + "/root/deploy/traces")
                        if os.path.exists("_node_stderr.txt"):
                            cmd = """ grep "HANDLE JOB:DOWNLOAD:file_hash" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            downloaded_files = []
                            for entry in sources_splitted:
                                first_split = entry.split(':')
                                job_id = first_split[5].split(" ")[2]
                                if job_id in jobID_set:
                                    if job_id not in dict_of_download_sources[filename]: dict_of_download_sources[
                                        filename].update({job_id: {}})
                                    file_hash = first_split[8].split(",")[0].split("=")[1]
                                    location = first_split[8].split(",")[1].split("=")[1]
                                    source = first_split[8].split(",")[2].split("=")[1]
                                    dict_of_download_sources[filename][job_id].update(
                                        {filename: (node, file_hash, location, source)})
                    already_done.add(filename.split("-")[1])

                    results.update({filename: {}})
                    xp_1 = filename
                    if "new" in filename:
                        xp_2 = filename.replace("new", "dht")
                    else:
                        xp_2 = filename.replace("dht", "new")
                    not_going_to_source = {xp_1: 0, xp_2: 0}
                    not_going_same_destination = 0
                    difference_processed_jobs = 0
                    for id in dict_of_download_sources[xp_1]:
                        if id in dict_of_download_sources[xp_1] and id in dict_of_download_sources[xp_2]:
                            if dict_of_download_sources[xp_1][id][xp_1][2] != dict_of_download_sources[xp_1][id][xp_1][
                                3]:
                                not_going_to_source[xp_1] += 1
                            if dict_of_download_sources[xp_2][id][xp_2][2] != dict_of_download_sources[xp_2][id][xp_2][
                                3]:
                                not_going_to_source[xp_2] += 1

                            if dict_of_download_sources[xp_1][id][xp_1][2] != dict_of_download_sources[xp_2][id][xp_2][
                                2]:
                                not_going_same_destination += 1
                        else:
                            difference_processed_jobs += 1
                    results[filename].update({'not_going_same_destination': not_going_same_destination,
                                              'not_going_to_source': not_going_to_source})
                    os.chdir(path)

print(json.dumps(results, indent=4))

# elif filename.startswith("dht"):
# 	os.chdir(path + "/" + filename + "/")
# 	if filename not in dict_of_download_sources: dict_of_download_sources.update({filename: {}})
# 	for node in os.listdir(os.getcwd()):
# 		os.chdir(path + "/" + filename + "/" + node + "/root/deploy/traces")
# 		cmd = """ grep "HANDLE JOB:DOWNLOAD:file_hash" _node_stderr.txt """
# 		sources = os.popen(cmd).read()
# 		sources_splitted = sources.split('\n')
# 		del sources_splitted[-1]
# 		downloaded_files = []
# 		for entry in sources_splitted:
# 			first_split = entry.split(':')
# 			job_id = first_split[5].split(" ")[2]
# 			if job_id not in dict_of_download_sources[filename]: dict_of_download_sources[filename].update({job_id: {'AAA': (), 'DHT': ()}})
# 			file_hash = first_split[8].split(",")[0].split("=")[1]
# 			location = first_split[8].split(",")[1].split("=")[1]
# 			source = first_split[8].split(",")[2].split("=")[1]
# 			dict_of_download_sources[filename][job_id]['DHT'] = (node, file_hash, location, source)
# 		print("lol")

# 	total_diff = 0
# 	total_length = 0
# 	for node in dict_of_download_sources:
# 		print(node)
# 		for i in range(len(dict_of_download_sources[node]['AAA'])):
# 			if dict_of_download_sources[node]['AAA'][i] != dict_of_download_sources[node]['DHT'][i]:
# 				total_diff += 1
# 				print(str(dict_of_download_sources[node]['AAA'][i]) + " - " + str(dict_of_download_sources[node]['DHT'][i]))
# 		total_length+= len(dict_of_download_sources[node]['AAA'])
#
# 	print(total_diff)
# 	print(total_length)
#
#
#
# os.chdir(path + "/new")
# dict_of_download_sources = {}
# for filename in os.listdir(os.getcwd()):
# 	if not filename.startswith('.'):
# 		os.chdir(path + "/new/" + filename + "/root/deploy/traces")
# 		if os.path.exists(os.getcwd() + "/_node_stderr.txt"):
# 			dict_of_download_sources.update({filename: {'AAA': [], 'DHT': []}})
# 			cmd = """ grep "from" _node_stderr.txt | awk -F":" '{print $7}' """
# 			sources = os.popen(cmd).read()
# 			sources_splitted = sources.split('\n')
# 			del sources_splitted[-1]
# 			downloaded_files = []
# 			for entry in sources_splitted:
# 				entry_splitted = entry.split('-')
# 				downloaded_files.append((entry_splitted[0], entry_splitted[1], entry_splitted[2]))
# 			dict_of_download_sources[filename]['AAA'] = downloaded_files
#
# os.chdir(path + "/dht")
# for filename in os.listdir(os.getcwd()):
# 	if not filename.startswith('.'):
# 		os.chdir(path + "/dht/" + filename + "/root/deploy/traces")
# 		if os.path.exists(os.getcwd() + "/_node_stderr.txt"):
# 			cmd = """ grep "from" _node_stderr.txt | awk -F":" '{print $7}' """
# 			sources = os.popen(cmd).read()
# 			sources_splitted = sources.split('\n')
# 			del sources_splitted[-1]
# 			downloaded_files = []
# 			for entry in sources_splitted:
# 				entry_splitted = entry.split('-')
# 				downloaded_files.append((entry_splitted[0], entry_splitted[1], entry_splitted[2]))
# 			dict_of_download_sources[filename]['DHT'] = downloaded_files
#
# total_diff = 0
# total_length = 0
# for node in dict_of_download_sources:
# 	print(node)
# 	for i in range(len(dict_of_download_sources[node]['AAA'])):
# 		if dict_of_download_sources[node]['AAA'][i] != dict_of_download_sources[node]['DHT'][i]:
# 			total_diff += 1
# 			print(str(dict_of_download_sources[node]['AAA'][i]) + " - " + str(dict_of_download_sources[node]['DHT'][i]))
# 	total_length+= len(dict_of_download_sources[node]['AAA'])
#
# print(total_diff)
# print(total_length)
#
#
# print("lol")
