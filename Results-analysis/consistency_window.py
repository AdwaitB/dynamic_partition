
import os
import json
from datetime import datetime
from statistics import mean, stdev
import matplotlib.pyplot as plt
import numpy as np

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater_full_log/"
# Get nbr of messages of AAA algo:
os.chdir(path)
# list_of_interval_names = [x.split('_')[5] for x in os.listdir(os.getcwd()) if not x.startswith(".")]

all_graphs_results = {}
list_of_interval = [x for x in os.listdir(os.getcwd()) if x.startswith("Renater")]
list_of_interval.sort(key=lambda x: float(x.split("_")[5][:-1]))
for interval in list_of_interval:
    all_graphs_results.update({interval: {}})
    print(interval)
    os.chdir(path + interval + "/transient")
    xp_path = os.getcwd()
    list_of_files = [x for x in os.listdir(os.getcwd())]
    list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
    cache_sizes = set([x.split("-")[1] for x in list_of_xps])
    os.chdir(xp_path)
    for filename in os.listdir(os.getcwd()):
        print(filename)
        if not filename.startswith('.'):
            if os.path.isdir(filename):
                if not filename.startswith("baseline"):
                    os.chdir(xp_path + "/" + filename + "/")
                    all_graphs_results[interval].update({filename: {}})
                    for node in os.listdir(os.getcwd()):
                        os.chdir(xp_path + "/" + filename + "/" + node + "/root/deploy/traces")
                        if os.path.exists("_node_stderr.txt"):
                            # Get the sent messages
                            cmd = """ grep "Put msg in queue" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            for entry in sources_splitted:
                                time_of_entry = datetime.fromisoformat(entry.split("root")[1].split("Put")[0][1:len(entry) - 1][:-2])
                                msg = eval(entry.split('Put msg in queue:')[1])
                                msg_string = tuple(sorted(msg.items()))
                                if msg_string not in all_graphs_results[interval][filename]: all_graphs_results[interval][filename].update({msg_string: {'sent': [], 'received': []}})
                                all_graphs_results[interval][filename][msg_string]['sent'].append(time_of_entry)

                            cmd = """ grep "request_json_list:" _node_stderr.txt """
                            sources = os.popen(cmd).read()
                            sources_splitted = sources.split('\n')
                            del sources_splitted[-1]
                            already_received = set()
                            for entry in sources_splitted:
                                time_of_entry = datetime.fromisoformat(entry.split("root")[1].split("Nb of JSON")[0][1:len(entry) - 1][:-2])
                                list_of_message = eval(entry.split('request_json_list:')[1])
                                for msg in list_of_message:
                                    msg_string = tuple(sorted(msg.items()))
                                    if msg_string not in all_graphs_results[interval][filename]: all_graphs_results[interval][filename].update({msg_string: {'sent': [], 'received': []}})
                                    if msg_string not in already_received:  # We do not count if we already have the info on the node
                                        all_graphs_results[interval][filename][msg_string]['received'].append(time_of_entry)
                                    already_received.add(msg_string)

                    list_of_delays = []
                    for msg in all_graphs_results[interval][filename]:
                        first_send = sorted(all_graphs_results[interval][filename][msg]['sent'])[0]
                        last_received = sorted(all_graphs_results[interval][filename][msg]['received'])[-1]
                        list_of_delays.append((last_received - first_send).total_seconds())

                    sorted_list_of_delays = sorted(list_of_delays)

                    num_bins = 10000
                    counts, bin_edges = np.histogram(sorted_list_of_delays, bins=num_bins, normed=True)
                    cdf = np.cumsum(counts)
                    plt.plot(bin_edges[1:], cdf / cdf[-1], label=interval+'-'+filename)
                    plt.legend()


                    os.chdir(xp_path)


font = {'family': 'normal',
        'size': 30}
plt.rc('font', **font)
plt.rcParams.update({'lines.linewidth': 6, "xtick.labelsize": 30, 'ytick.labelsize': 30})
plt.xlabel("Maximum inconsistency window (seconds)", fontsize=30)
plt.ylabel("CDF", fontsize=30)
plt.show()

# import os
# import json
# from datetime import datetime
# from statistics import mean, stdev
# import matplotlib.pyplot as plt
# import numpy as np
#
# path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater_full_log/"
# # Get nbr of messages of AAA algo:
# os.chdir(path)
# # list_of_interval_names = [x.split('_')[5] for x in os.listdir(os.getcwd()) if not x.startswith(".")]
#
# all_graphs_results = {}
# list_of_interval = [x for x in os.listdir(os.getcwd()) if x.startswith("Renater")]
# list_of_interval.sort(key=lambda x: float(x.split("_")[5][:-1]))
# for interval in list_of_interval:
#     all_graphs_results.update({interval: {}})
#     print(interval)
#     os.chdir(path + interval + "/transient")
#     xp_path = os.getcwd()
#     list_of_files = [x for x in os.listdir(os.getcwd())]
#     list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
#     cache_sizes = set([x.split("-")[1] for x in list_of_xps])
#     os.chdir(xp_path)
#     for filename in os.listdir(os.getcwd()):
#         print(filename)
#         if not filename.startswith('.'):
#             if os.path.isdir(filename):
#                 if not filename.startswith("baseline"):
#                     os.chdir(xp_path + "/" + filename + "/")
#                     all_graphs_results[interval].update({filename: {}})
#                     for node in os.listdir(os.getcwd()):
#                         os.chdir(xp_path + "/" + filename + "/" + node + "/root/deploy/traces")
#                         if os.path.exists("_node_stderr.txt"):
#                             # Get the sent messages
#                             cmd = """ grep "Put msg in queue" _node_stderr.txt """
#                             sources = os.popen(cmd).read()
#                             sources_splitted = sources.split('\n')
#                             del sources_splitted[-1]
#                             for entry in sources_splitted:
#                                 time_of_entry = datetime.fromisoformat(entry.split("root")[1].split("Put")[0][1:len(entry) - 1][:-2])
#                                 list_of_message = eval(entry.split('Put msg in queue:')[1])
#                                 for msg in list_of_message:
#                                     msg_string = tuple(sorted(msg.items()))
#                                     if msg_string not in all_graphs_results[interval][filename]: all_graphs_results[interval][filename].update({msg_string: {'sent': [], 'received': []}})
#                                     all_graphs_results[interval][filename][msg_string]['sent'].append(time_of_entry)
#
#                             cmd = """ grep "request_json_list:" _node_stderr.txt """
#                             sources = os.popen(cmd).read()
#                             sources_splitted = sources.split('\n')
#                             del sources_splitted[-1]
#                             already_received = set()
#                             for entry in sources_splitted:
#                                 time_of_entry = datetime.fromisoformat(entry.split("root")[1].split("Nb of JSON")[0][1:len(entry) - 1][:-2])
#                                 list_of_message = eval(entry.split('request_json_list:')[1])
#                                 for msg in list_of_message:
#                                     msg_string = tuple(sorted(msg.items()))
#                                     if msg_string not in all_graphs_results[interval][filename]: all_graphs_results[interval][filename].update({msg_string: {'sent': [], 'received': []}})
#                                     if msg_string not in already_received:  # We do not count if we already have the info on the node
#                                         all_graphs_results[interval][filename][msg_string]['received'].append(time_of_entry)
#                                     already_received.add(msg_string)
#
#                     list_of_delays = []
#                     for msg in all_graphs_results[interval][filename]:
#                         first_send = sorted(all_graphs_results[interval][filename][msg]['sent'])[0]
#                         last_received = sorted(all_graphs_results[interval][filename][msg]['received'])[-1]
#                         list_of_delays.append((last_received - first_send).total_seconds())
#
#                     sorted_list_of_delays = sorted(list_of_delays)
#
#                     num_bins = 10000
#                     counts, bin_edges = np.histogram(sorted_list_of_delays, bins=num_bins, normed=True)
#                     cdf = np.cumsum(counts)
#                     plt.plot(bin_edges[1:], cdf / cdf[-1], label=interval+'-'+filename)
#                     plt.legend()
#                     plt.show()
#
#                     os.chdir(xp_path)
#                     print('lol')
