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
list_of_interval.sort(key=lambda x: float(x.split("_")[5][:-1]))

dict_nb_messages = {}
dict_nb_errors = {}
NB_JOBS = 20000
if not os.path.exists("dict_nb_messages.json"):
    for interval in list_of_interval:
        print(interval)
        dict_nb_messages.update({interval: {}})
        dict_nb_errors.update({interval: {}})
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

            # Get nbr of errors
            cmd = """ grep -r "Error 404" . | wc -l """
            nb_errors = int(os.popen(cmd).read())
            dict_nb_errors[interval][filename] = round(float(nb_errors * 100) / (float(NB_JOBS)), 1)

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
                            if entry.split(',')[2].split(":")[1] != entry.split('\n')[0].split(',')[3].split(":")[1]:
                                dict_nb_messages[interval][filename][node]['sent_req'] += 1
            #os.chdir(xp_path)

    #Save dict to debug
    os.chdir(path)
    with open('dict_nb_messages.json', 'w') as fp:
        json.dump(dict_nb_messages, fp)

    # Save dict to debug
    os.chdir(path)
    with open('dict_nb_errors.json', 'w') as fp:
        json.dump(dict_nb_errors, fp)
#

cache_sizes = ['20', '40', '60']
# # analyse the data
os.chdir(path)
with open('dict_nb_messages.json') as json_file:
    dict_nb_messages = json.load(json_file)

with open('dict_nb_errors.json') as json_file:
    dict_nb_errors = json.load(json_file)


plt.rcParams.update({'font.size': 30, 'lines.linewidth' : 3, "xtick.labelsize" : 20, 'ytick.labelsize' : 20})
fig, ax1 = plt.subplots()

ylim = 22000
ax1.set_xlabel('Update interval (seconds)')
ax1.set_ylabel('Average number of received messages per node')
#ax1.set_ylim(bottom=0, top=ylim)


to_plot = {}
x_labels = [x.split('_')[5] for x in list_of_interval]
cache_sizes = sorted(list(cache_sizes))
for size in cache_sizes:
    to_plot.update({size: {'aaa': [], 'dht': []}})
    for interval in list_of_interval:
        list_of_nodes = [x for x in dict_nb_messages[interval]["dht-{}-{}".format(size, interval.split("_")[5])].keys()]
        y_dht = [dict_nb_messages[interval]["dht-{}-{}".format(size, interval.split("_")[5])][x]['received_msg'] for x in list_of_nodes]
        y_aaa = [dict_nb_messages[interval]["new-{}-{}".format(size, interval.split("_")[5])][x]['received_msg'] for x in list_of_nodes]
        dht_average = mean(y_dht)
        aaa_average = mean(y_aaa)
        to_plot[size]['aaa'].append(aaa_average)
        to_plot[size]['dht'].append(dht_average)
    ax1.plot(x_labels, to_plot[size]['aaa'], label='aaa - {}'.format(size), marker="o", markersize=7, linestyle="-.")
    ax1.plot(x_labels, to_plot[size]['dht'], label='dht - {}'.format(size), marker="x", markersize=7, linestyle="--")
    ax1.legend(loc='upper left', bbox_to_anchor=(0.65, 1))

#ax1.set_yticks(range(0, ylim, 250), minor=True)

axes = plt.gca()
axes.yaxis.grid(which='minor')

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax2.set_ylabel('Cache miss ratio - (Fall back to source)')  # we already handled the x-label with ax1
ax2.set_ylim(bottom=0, top=27)
ax2.set_yticks(range(0, 27, 1), minor=True)

ticks_sp = [i for i in range(0, len(x_labels))]
barWidth = 0.05
i = -len(cache_sizes)
to_plot_errors = {}
for size in cache_sizes:
    to_plot_errors.update({size: {'aaa': [], 'dht': []}})
    for interval in list_of_interval:
        to_plot_errors[size]['aaa'].append(dict_nb_errors[interval]["new-{}-{}".format(size, interval.split("_")[5])])
        to_plot_errors[size]['dht'].append(dict_nb_errors[interval]["dht-{}-{}".format(size, interval.split("_")[5])])
    x_ticks = [x + i*barWidth for x in ticks_sp]
    ax2.bar(x_ticks, to_plot_errors[size]['aaa'], label='aaa - {}'.format(size), width=barWidth, edgecolor='black')
    i += 1
    x_ticks = [x + i*barWidth for x in ticks_sp]
    ax2.bar(x_ticks, to_plot_errors[size]['dht'], label='dht - {}'.format(size), width=barWidth, hatch='//', edgecolor='black')
    ax2.legend()
    i += 1

plt.gca().set_yticklabels(['{:.0f}%'.format(x) for x in plt.gca().get_yticks()])
fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.legend()


ax1.set_yscale('log')
ax1.set_ylim(bottom=100)
#plt.title("Tradeoff between number of exchanged messages and number of 404 errors - {} Jobs".format(NB_JOBS))
plt.show()


# font = {'family' : 'normal',
#         'size'   : 22}
# plt.rc('font', **font)
# plt.rcParams.update({'lines.linewidth' : 7, "xtick.labelsize" : 40, 'ytick.labelsize' : 40})

font = {'family': 'normal',
        'size': 30}
plt.rc('font', **font)
plt.rcParams.update({'lines.linewidth': 6, "xtick.labelsize": 30, 'ytick.labelsize': 30})

# Plot the number of messages per IP packet:
to_plot_nb_messages = {}
x_labels = [x.split('_')[5] for x in list_of_interval]
cache_sizes = sorted(list(cache_sizes))
for size in cache_sizes:
    to_plot_nb_messages.update({size: {'aaa': [], 'dht': []}})
    for interval in list_of_interval:
        list_of_nodes = [x for x in dict_nb_messages[interval]["dht-{}-{}".format(size, interval.split("_")[5])].keys()]
        y_dht = [mean(dict_nb_messages[interval]["dht-{}-{}".format(size, interval.split("_")[5])][x]['sent_msg']) for x in list_of_nodes]
        y_aaa = [mean(dict_nb_messages[interval]["new-{}-{}".format(size, interval.split("_")[5])][x]['sent_msg']) for x in list_of_nodes]
        dht_average = mean(y_dht)
        aaa_average = mean(y_aaa)
        to_plot_nb_messages[size]['aaa'].append(aaa_average)
        to_plot_nb_messages[size]['dht'].append(dht_average)
    plt.plot(x_labels, to_plot_nb_messages[size]['aaa'], label='aaa - {}'.format(size), marker="o", markersize=15)
    plt.plot(x_labels, to_plot_nb_messages[size]['dht'], label='dht - {}'.format(size), marker="x", markersize=15)
axes = plt.gca()
axes.yaxis.grid()
plt.legend()
plt.xlabel("Update interval (seconds)", fontsize=30)
plt.ylabel("Average number of updates in a single IP packet", fontsize=30)
#plt.title("Impact of the request time to get an object for DHT and AAA for different cache sizes")
plt.yticks(range(0, 27, 1), ["0", "", "", "", "", "5", "", "", "", "" "10", "", "", "", "", "15", "", "", "", "", "20", "", "", "", "", "25"])

plt.show()

