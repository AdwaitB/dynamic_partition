import os
from datetime import datetime
from statistics import mean, stdev

# GEt the DATA
path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/Jobs_50ms/transient"
# Get nbr of messages of AAA algo:
os.chdir(path)
list_of_files = [x for x in os.listdir(os.getcwd())]
list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
cache_sizes = set([x.split("-")[1] for x in list_of_xps])
results = {}
already_done = set()
dict_of_times = {}
for filename in list_of_xps:
    print(filename)
    os.chdir(path + "/" + filename + "/")
    if filename not in dict_of_times: dict_of_times.update({filename: {}})
    for node in os.listdir(os.getcwd()):
        dict_of_times[filename].update({node: {}})
        os.chdir(path + "/" + filename + "/" + node + "/root/deploy/traces")
        if os.path.exists("_node_stderr.txt"):
            cmd = """ grep "HANDLE JOB:DOWNLOAD:file_hash" _node_stderr.txt """
            insert_times = os.popen(cmd).read()
            insert_times_splitted = insert_times.split('\n')
            del insert_times_splitted[-1]
            for entry in insert_times_splitted:
                time_of_entry = datetime.fromisoformat(entry.split("root")[1].split("JOB")[0][1:len(entry) - 1][:-1])
                file_hash = entry.split("file_hash")[1].split(',')[0][3:]
                if file_hash not in dict_of_times[filename][node]:
                    dict_of_times[filename][node].update({file_hash: []})
                dict_of_times[filename][node][file_hash].append((0,time_of_entry))

            cmd = """ grep "Error 404" _node_stderr.txt """
            insert404 = os.popen(cmd).read()
            insert404_splitted = insert404.split('\n')
            del insert404_splitted[-1]
            for entry in insert404_splitted:
                time_of_insert = datetime.fromisoformat(entry.split("root")[1].split("JOB")[0][1:len(entry) - 1][:-1])
                file_hash = entry.split("file_hash")[1].split(',')[0][3:]
                if file_hash not in dict_of_times[filename][node]:
                    dict_of_times[filename][node].update({file_hash: []})
                dict_of_times[filename][node][file_hash].append((0,time_of_insert))

            cmd = """ grep "TRIGGER REMOVE" _node_stderr.txt """
            remove_times = os.popen(cmd).read()
            remove_times_splitted = remove_times.split('\n')
            del remove_times_splitted[-1]
            for entry in remove_times_splitted:
                time_of_remove = datetime.fromisoformat(entry.split("root")[1].split("JOB")[0][1:len(entry) - 1][:-1])
                if filename.startswith("new"):
                    file_hash = entry.split("=")[1][1:]
                elif filename.startswith("dht"):
                    file_hash = entry.split("=")[1][1:].split(",")[0]
                dict_of_times[filename][node][file_hash].append((1,time_of_remove))

times_in_cache = {}
total_time_in_cache = {}
for filename in list_of_xps:
    times_in_cache.update({filename: {}})
    total_time_in_cache.update({filename: []})
    for node in dict_of_times[filename]:
        times_in_cache[filename].update({node: []})
        for hash in dict_of_times[filename][node]:
            dict_of_times[filename][node][hash] = sorted(dict_of_times[filename][node][hash], key=lambda x: x[1])
            if len(dict_of_times[filename][node][hash]) % 2 != 0: del dict_of_times[filename][node][hash][-1]  # Remove last ADD because end of the XP
            for i in range(0,len(dict_of_times[filename][node][hash]) - 1, 2):
                times_in_cache[filename][node].append((dict_of_times[filename][node][hash][i+1][1] - dict_of_times[filename][node][hash][i][1]).total_seconds())
                total_time_in_cache[filename].append((dict_of_times[filename][node][hash][i+1][1] - dict_of_times[filename][node][hash][i][1]).total_seconds())
    print(filename)
    print(mean(total_time_in_cache[filename]))
    print(stdev(total_time_in_cache[filename]))
    print("-----")



