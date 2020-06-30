import os
import json
from oracle import get_optimal_destination



path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater_random_interval/t "
# # Genbr of messages of AAA algo:
os.chdir(path)
#list_of_interval_names = [x.split('_')[5] for x in os.listdir(os.getcwd()) if not x.startswith(".")]

all_graphs_results = {}
list_of_interval = [x for x in os.listdir(os.getcwd()) if x.startswith("Renater")]
list_of_interval.sort(key=lambda x: float(x.split("_")[5][:-1]))
for interval in list_of_interval:
    all_graphs_results.update({interval: {}})
    print(interval)
    os.chdir(path+interval+"/transient")
    xp_path = os.getcwd()
    list_of_files = [x for x in os.listdir(os.getcwd())]
    list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
    cache_sizes = set([x.split("-")[1] for x in list_of_xps])

    optimal_dest = get_optimal_destination(xp_path)
    
    os.chdir(xp_path)
    with open('oracle.json', 'w') as fp:
        json.dump(optimal_dest, fp)
    
    os.chdir(xp_path)
    dict_of_download_sources = {}
    results = {}
    already_done = set()
    NB_JOBS = 20000
    difference_from_oracle = {}
    for filename in os.listdir(os.getcwd()):
        print(filename)
        if not filename.startswith('.'):
            if os.path.isdir(filename):
                if not filename.startswith("baseline"):
                    os.chdir(xp_path + "/" + filename + "/")
                    if filename not in dict_of_download_sources: dict_of_download_sources.update({filename: {}})
                    for node in os.listdir(os.getcwd()):
                        os.chdir(xp_path + "/" + filename + "/" + node + "/root/deploy/traces")
                        if os.path.exists("_node_stderr.txt"):
                            cmd = """ grep "HANDLE JOB:DOWNLOAD:file_hash" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            downloaded_files = []
                            for entry in sources_splitted:
                                first_split = entry.split(':')
                                job_id = int(first_split[5].split(" ")[2])
                                if job_id not in dict_of_download_sources[filename]: dict_of_download_sources[filename].update({job_id: ""})
                                file_hash = first_split[8].split(",")[0].split("=")[1]
                                location = first_split[8].split(",")[1].split("=")[1]
                                source = first_split[8].split(",")[2].split("=")[1]
                                dict_of_download_sources[filename][job_id] = location
    
                            cmd = """ grep "Error 404 Fall back to source" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            downloaded_files = []
                            for entry in sources_splitted:
                                first_split = entry.split(':')
                                job_id = int(first_split[5].split(" ")[2])
                                if job_id not in dict_of_download_sources[filename]: dict_of_download_sources[filename].update({job_id: ""})
                                source = entry.split("source_ip = ")[1]
                                dict_of_download_sources[filename][job_id] = source  # We go to the source here after a 404 error
    
                    difference_from_oracle.update({filename: 0})
                    for job_id in optimal_dest[filename]:
                        if optimal_dest[filename][job_id].strip() != dict_of_download_sources[filename][job_id].strip():
                            difference_from_oracle[filename] += 1
    
                    os.chdir(xp_path)
    
    print(json.dumps(difference_from_oracle, indent = 4))
    
    difference_in_percent = {}
    for xp in difference_from_oracle:
        difference_in_percent.update({xp: round(float(difference_from_oracle[xp] * 100) / float(NB_JOBS), 1)})
    
    print(json.dumps(difference_in_percent, indent = 4))
    print('lol')
    all_graphs_results[interval] = difference_in_percent

os.chdir(path)
with open('best_miss_ration.json', 'w') as fp:
    json.dump(all_graphs_results, fp)