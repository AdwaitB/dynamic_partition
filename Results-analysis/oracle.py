import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import statistics
import sys
import json
from LRU import LRUCache
from time import sleep
import concurrent.futures
import random
import time


all_pairs_SPT_latencies = {}
SEED = 123
random.seed(SEED)
step = 50
upper = 50
N_JOBS = 20000

def get_closest_copy(requesting_ip, available_nodes):
    closest_copy = available_nodes[0]
    min_distance = all_pairs_SPT_latencies[requesting_ip][closest_copy]
    for node in available_nodes:
        if all_pairs_SPT_latencies[requesting_ip][node] < min_distance:
            min_distance = all_pairs_SPT_latencies[requesting_ip][node]
            closest_copy = node
    return closest_copy


def update_conf(dict_of_nodes, requesting_ip, file_hash,file_size, configuration):
    # Update the configuration
    removed_hash = dict_of_nodes[requesting_ip].set(file_hash, file_size)
    configuration[file_hash].append(requesting_ip)
    if removed_hash != 0:
        try:
            configuration[removed_hash].remove(requesting_ip)
        except ValueError:
            sys.exit("Tried to removed a hash that was not present in cache...")


def get_all_pairs_SPT(path):
    os.chdir(path)
    cmd = """ find  ./* -name "_node_stdout.txt" """
    data_path = os.popen(cmd).read()
    data_path = data_path.split("\n")
    with open(data_path[0], 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line with "shorted path dist"
        string_dict = ""
        for row in reader:
            if row[0] == "shortest_paths":
                break
            else:
                string_dict += row[0] + ","
    string_dict = string_dict.replace("\'", "\"")[:-1]
    return json.loads(string_dict)


def get_optimal_destination(path):
    global all_pairs_SPT_latencies
    all_pairs_SPT_latencies = get_all_pairs_SPT(path)

    # Get the source mapping
    os.chdir(path)
    cmd = """ find  ./* -name "traces.json" """
    data_path = os.popen(cmd).read()
    data_path = data_path.split("\n")
    with open(data_path[0]) as json_file:
        dict_sources = json.load(json_file)
    mapping = dict_sources['CONTROL_ENTRIES'][0]['mapping']

    # Get the trace to replay, i.e. the file hash and the requesting IP for each JOB_ID
    os.chdir(path)
    cmd = """ find  ./* -name "traces_*.csv" """
    data_path = os.popen(cmd).read()
    data_path = data_path.split("\n")
    data_path = [x for x in data_path if "small" not in x and x != """""""" and "baseline" not in x]
    trace = {}
    best_location = {}
    for csv_file in data_path:
        if len(csv_file.split("_")[1].split(".")) == 3:
            xp_name = csv_file.split("_")[1].split(".")[0] + "." + csv_file.split("_")[1].split(".")[1] # To handle the 0.001s case
        else:
            xp_name = csv_file.split("_")[1].split(".")[0]
        cache_size = int(csv_file.split("_")[1].split(".")[0].split("-")[1])
        trace[xp_name] = {}
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the first line with names of columns
            for row in reader:
                job_id = float(row[3])
                trace[xp_name].update({job_id: {"file_hash": row[2], "ip": row[1], 'download_time': row[7]}})

        # Initial configuration with each filehash initialized with the source node.
        configuration = {}
        dict_of_nodes = {}
        for file_hash in mapping:
            configuration.update({file_hash: [mapping[file_hash]['source']]})
            dict_of_nodes.update({mapping[file_hash]['source']: LRUCache(cache_size)})

        # Replay the trace
        best_location.update({xp_name: {}})
        list_of_events = []
        wait = 0
        for i in range(N_JOBS):
            list_of_events.append((wait, "JOB", i))
            if i in trace[xp_name]:
                file_size = 0  # We do not care about fle size here
                file_hash = trace[xp_name][i]['file_hash'].split('.')[0]
                requesting_ip = trace[xp_name][i]['ip']
                download_time = float(trace[xp_name][i]['download_time'])
                list_of_events.append((wait+download_time, "UPDATE", requesting_ip, file_hash, file_size))
            wait += (random.uniform(0, float(upper) / 1000) + float(step) / 1000)

        list_of_events = sorted(list_of_events, key=lambda event: event[0])

        for event in list_of_events:
            if event[1] == "JOB":
                if event[2] in trace[xp_name]:
                    file_hash = trace[xp_name][event[2]]['file_hash'].split('.')[0]
                    requesting_ip = trace[xp_name][event[2]]['ip']
                    file_size = 0
                    closest_copy = get_closest_copy(requesting_ip, configuration[file_hash])
                    best_location[xp_name].update({int(event[2]): closest_copy})
            else:  # Cache update
                file_hash = event[3]
                requesting_ip = event[2]
                file_size = 0
                update_conf(dict_of_nodes, requesting_ip, file_hash, file_size, configuration)

    return best_location


# import matplotlib.pyplot as plt
# import numpy as np
# import csv
# import os
# import statistics
# import sys
# import json
# from LRU import LRUCache
# from time import sleep
# import concurrent.futures
# import random
# import time
#
#
# all_pairs_SPT_latencies = {}
# SEED = 123
# random.seed(SEED)
# step = 50
# upper = 50
# N_JOBS = 20000
#
# def get_closest_copy(requesting_ip, available_nodes):
#     closest_copy = available_nodes[0]
#     min_distance = all_pairs_SPT_latencies[requesting_ip][closest_copy]
#     for node in available_nodes:
#         if all_pairs_SPT_latencies[requesting_ip][node] < min_distance:
#             min_distance = all_pairs_SPT_latencies[requesting_ip][node]
#             closest_copy = node
#     return closest_copy
#
#
# def update_conf(dict_of_nodes, requesting_ip, file_hash,file_size, configuration, download_time):
#     # Update the configuration
#     sleep(download_time)
#     removed_hash = dict_of_nodes[requesting_ip].set(file_hash, file_size)
#     configuration[file_hash].append(requesting_ip)
#     if removed_hash != 0:
#         try:
#             configuration[removed_hash].remove(requesting_ip)
#         except ValueError:
#             sys.exit("Tried to removed a hash that was not present in cache...")
#
#
# def get_all_pairs_SPT(path):
#     os.chdir(path)
#     cmd = """ find  ./* -name "_node_stdout.txt" """
#     data_path = os.popen(cmd).read()
#     data_path = data_path.split("\n")
#     with open(data_path[0], 'r') as file:
#         reader = csv.reader(file)
#         next(reader)  # Skip the first line with "shorted path dist"
#         string_dict = ""
#         for row in reader:
#             if row[0] == "shortest_paths":
#                 break
#             else:
#                 string_dict += row[0] + ","
#     string_dict = string_dict.replace("\'", "\"")[:-1]
#     return json.loads(string_dict)
#
#
# def get_optimal_destination(path):
#     global all_pairs_SPT_latencies
#     all_pairs_SPT_latencies = get_all_pairs_SPT(path)
#
#     # Get the source mapping
#     os.chdir(path)
#     cmd = """ find  ./* -name "traces.json" """
#     data_path = os.popen(cmd).read()
#     data_path = data_path.split("\n")
#     with open(data_path[0]) as json_file:
#         dict_sources = json.load(json_file)
#     mapping = dict_sources['CONTROL_ENTRIES'][0]['mapping']
#
#     # Get the trace to replay, i.e. the file hash and the requesting IP for each JOB_ID
#     os.chdir(path)
#     cmd = """ find  ./* -name "traces_*.csv" """
#     data_path = os.popen(cmd).read()
#     data_path = data_path.split("\n")
#     data_path = [x for x in data_path if "small" not in x and x != """""""" and "baseline" not in x]
#     trace = {}
#     best_location = {}
#     for csv_file in data_path:
#         xp_name = csv_file.split("_")[1].split(".")[0]
#         cache_size = int(csv_file.split("_")[1].split(".")[0].split("-")[1])
#         trace[xp_name] = {}
#         with open(csv_file, 'r') as file:
#             reader = csv.reader(file)
#             next(reader)  # Skip the first line with names of columns
#             for row in reader:
#                 job_id = float(row[3])
#                 trace[xp_name].update({job_id: {"file_hash": row[2], "ip": row[1], 'download_time': row[7]}})
#
#         # Initial configuration with each filehash initialized with the source node.
#         configuration = {}
#         dict_of_nodes = {}
#         for file_hash in mapping:
#             configuration.update({file_hash: [mapping[file_hash]['source']]})
#             dict_of_nodes.update({mapping[file_hash]['source']: LRUCache(cache_size)})
#
#         # Replay the trace
#         best_location.update({xp_name: {}})
#         for i in range(N_JOBS):
#             wait = (random.uniform(0, float(upper) / 1000) + float(step) / 1000)
#             print(str(i)+ " - wait: " + str(wait))
#             time.sleep(wait)
#             if i in trace[xp_name]:
#                 file_size = 0  # We do not care about fle size here
#                 file_hash = trace[xp_name][job_id]['file_hash'].split('.')[0]
#                 requesting_ip = trace[xp_name][job_id]['ip']
#                 closest_copy = get_closest_copy(requesting_ip, configuration[file_hash])
#                 download_time = trace[xp_name][job_id]['download_time']
#                 executor = concurrent.futures.ThreadPoolExecutor(max_workers=100)
#                 executor.submit(update_conf, dict_of_nodes, requesting_ip, file_hash, file_size, configuration, download_time)
#                 best_location[xp_name].update({int(job_id): closest_copy})
#
#     return best_location


# # Replay the trace
# best_location.update({xp_name: {}})
# file_size = 0  # We do not care about fle size here
# for job_id in sorted(list(trace[xp_name])):
#     file_hash = trace[xp_name][job_id]['file_hash'].split('.')[0]
#     requesting_ip = trace[xp_name][job_id]['ip']
#     closest_copy = get_closest_copy(requesting_ip, configuration[file_hash])
#     #print(configuration[file_hash])
#     # Update the configuration
#     removed_hash = dict_of_nodes[requesting_ip].set(file_hash, file_size)
#     configuration[file_hash].append(requesting_ip)
#     if removed_hash != 0:
#         try:
#             configuration[removed_hash].remove(requesting_ip)
#         except ValueError:
#             sys.exit("Tried to removed a hash that was not present in cache...")
#     best_location[xp_name].update({int(job_id): closest_copy})

if __name__ == '__main__':
    # Get the SPT
    path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/Renater20000Jobs_Cache20_40_60_seed777_5s"
    graph_name = '/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Topologies/Renater2010.gml'
    optimal_dest = get_optimal_destination(path)
    print("lol")
# # Check that all the jobs trace are the same in all xps
# intersection_job_id = set.intersection(set(trace['dht-60-3s']), set(trace['dht-40-3s']), set(trace['dht-20-3s']), set(trace['new-60-3s']), set(trace['new-40-3s']), set(trace['new-20-3s']))
# for job_id in intersection_job_id:
#     if not trace['dht-60-3s'][job_id] == trace['dht-40-3s'][job_id] == trace['dht-20-3s'][job_id] == trace['new-60-3s'][job_id] == trace['new-40-3s'][job_id] == trace['new-20-3s'][job_id]:
#         sys.exit("Seed looks different....")

