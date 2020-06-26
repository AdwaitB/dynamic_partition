import os
import matplotlib.pyplot as plt
from statistics import mean, stdev, pstdev
import json

#path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_5s/Renater20000Jobs_Cache20_40_60_seed777_5s/transient"
path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/"
# Get nbr of messages of AAA algo:
os.chdir(path)
#list_of_interval_names = [x.split('_')[5] for x in os.listdir(os.getcwd()) if not x.startswith(".")]


list_of_interval = [x for x in os.listdir(os.getcwd()) if x.startswith("Renater")]
list_of_interval.sort(key=lambda x: int(x.split("_")[5][:-1]))

dict_nb_messages = {}

if not os.path.exists("dict_nb_messages.json"):
    for interval in list_of_interval:
        print(interval)
        dict_nb_messages.update({interval: {}})
        os.chdir(path+interval+"/transient")
        xp_path = os.getcwd()
        list_of_files = [x for x in os.listdir(os.getcwd())]
        list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
        cache_sizes = set([x.split("-")[1] for x in list_of_xps])

        results = {}
        already_done = set()
        for filename in list_of_xps:
            print(filename)
            os.chdir(xp_path + "/" + filename + "/")
            if filename not in dict_nb_messages[interval]: dict_nb_messages[interval].update({filename: {}})
            for node in os.listdir(os.getcwd()):
                os.chdir(xp_path + "/" + filename + "/" + node + "/root/deploy/traces")
                if os.path.exists("_node_stderr.txt"):
                    cmd = """ grep "Nb of JSON" _node_stderr.txt | wc -l """
                    nbr_messages = int(os.popen(cmd).read())

                    if filename.startswith("dht"):  # We need to add the request messages to get the localization.
                        cmd = """ grep "HANDLE DHT:REQUEST" _node_stderr.txt | wc -l """
                        nbr_messages_req = int(os.popen(cmd).read())
                        nbr_messages = nbr_messages + nbr_messages_req

                    dict_nb_messages[interval][filename].update({node: {'received_msg': nbr_messages, 'sent_msg': [], 'sent_req': 0}})

                    cmd = """ grep "nb_of_msgs:" _node_stderr.txt """
                    sent_msg = os.popen(cmd).read()
                    sent_msg_splitted = sent_msg.split('\n')
                    del sent_msg_splitted[-1]
                    for entry in sent_msg_splitted:
                        nbr_sent_messages = entry.split(':')[8].split("-")[0]
                        dict_nb_messages[interval][filename][node]['sent_msg'].append(int(nbr_sent_messages))

                    if filename.startswith("dht"):  # We need to add the request messages to get the localization for DHT
                        cmd = """ grep "DEBUG:DHT:req_time" _node_stderr.txt """
                        sent_requests = os.popen(cmd).read()
                        sent_requests_splitted = sent_requests.split('\n')
                        del sent_requests_splitted[-1]
                        for entry in sent_requests_splitted:
                            # if entry.split(',')[2].split(":")[1] != entry.split('\n')[0].split(',')[3].split(":")[1]:
                            dict_nb_messages[interval][filename][node]['sent_req'] += 1
            #os.chdir(xp_path)

    #Save dict to debug
    os.chdir(path)
    with open('dict_nb_messages.json', 'w') as fp:
        json.dump(dict_nb_messages, fp)
#

cache_sizes = ['20', '40', '60']
# # analyse the data
os.chdir(path)
with open('dict_nb_messages.json') as json_file:
    dict_nb_messages = json.load(json_file)

to_plot = {}
x_labels = [x.split('_')[5] for x in list_of_interval]
cache_sizes = sorted(list(cache_sizes))
for size in cache_sizes:
    to_plot.update({size: {'aaa': [], 'dht': []}})
    for interval in list_of_interval:
        list_of_nodes = [x for x in dict_nb_messages[interval]["dht-{}".format(size)].keys()]
        y_dht = [dict_nb_messages[interval]["dht-{}".format(size)][x]['received_msg'] for x in list_of_nodes]
        y_aaa = [dict_nb_messages[interval]["new-{}".format(size)][x]['received_msg'] for x in list_of_nodes]
        dht_average = mean(y_dht)
        aaa_average = mean(y_aaa)
        to_plot[size]['aaa'].append(aaa_average)
        to_plot[size]['dht'].append(dht_average)
    plt.plot(x_labels, to_plot[size]['aaa'], label='aaa - {}'.format(size))
    plt.plot(x_labels, to_plot[size]['dht'], label='dht - {}'.format(size))

axes = plt.gca()
axes.yaxis.grid()
plt.legend()
plt.xlabel("Update interval (seconds)")
plt.ylabel("Average number of received messages per node")
plt.title("Total GET time reduction (in percent) when comparing DHT to AAA for different cache sizes")
plt.show()

        #print("Cache {} - Number of received messages:".format(size))
        #print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
        #print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))
