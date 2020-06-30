import os
import matplotlib.pyplot as plt
from statistics import mean, stdev, pstdev
import json


# Show the number of messages for a given time interval.
initial_path = os.getcwd()

# GEt the DATA
path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/JOBS_50ms/Renater20000Jobs_Cache20_40_60_seed777_3s/transient"
# Get nbr of messages of AAA algo:
os.chdir(path)
list_of_files = [x for x in os.listdir(os.getcwd())]
list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
cache_sizes = set([x.split("-")[1] for x in list_of_xps])
update_interval = list_of_xps[0].split("-")[2]
dict_nb_messages = {}
results = {}
already_done = set()
for filename in list_of_xps:
    print(filename)
    os.chdir(path + "/" + filename + "/")
    if filename not in dict_nb_messages: dict_nb_messages.update({filename: {}})
    for node in os.listdir(os.getcwd()):
        os.chdir(path + "/" + filename + "/" + node + "/root/deploy/traces")
        if os.path.exists("_node_stderr.txt"):
            cmd = """ grep "Nb of JSON" _node_stderr.txt | wc -l """
            nbr_messages = int(os.popen(cmd).read())

            dict_nb_messages[filename].update({node: {'received_msg': nbr_messages, 'received_msg_req': 0, 'sent_msg': [], 'sent_req': 0}})

            if filename.startswith("dht"):  # We need to add the request messages to get the localization.
                cmd = """ grep "HANDLE DHT:REQUEST" _node_stderr.txt | wc -l """
                nbr_messages_req = int(os.popen(cmd).read())
                #nbr_messages = nbr_messages + nbr_messages_req

                dict_nb_messages[filename][node]['received_msg_req'] = nbr_messages_req

            cmd = """ grep "nb_of_msgs:" _node_stderr.txt """
            sent_msg = os.popen(cmd).read()
            sent_msg_splitted = sent_msg.split('\n')
            del sent_msg_splitted[-1]
            for entry in sent_msg_splitted:
                nbr_sent_messages = entry.split(':')[8].split("-")[0]
                dict_nb_messages[filename][node]['sent_msg'].append(int(nbr_sent_messages))

            if filename.startswith("dht"):  # We need to add the request messages to get the localization for DHT
                cmd = """ grep "DEBUG:DHT:req_time" _node_stderr.txt """
                sent_requests = os.popen(cmd).read()
                sent_requests_splitted = sent_requests.split('\n')
                del sent_requests_splitted[-1]
                for entry in sent_requests_splitted:
                    # if entry.split(',')[2].split(":")[1] != entry.split('\n')[0].split(',')[3].split(":")[1]:
                    dict_nb_messages[filename][node]['sent_req'] += 1
#

# Save dict to debug
# os.chdir(initial_path)
# with open('dict_nb_messages.json', 'w') as fp:
#     json.dump(dict_nb_messages, fp)
#
# filename = list_of_xps[0]
# # analyse the data
# os.chdir(initial_path)
# with open('dict_nb_messages.json') as json_file:
#     dict_nb_messages = json.load(json_file)

x_label = sorted(list(cache_sizes))
# set width of bar
barWidth = 0.25

# Set position of bar on X axis
ticks_sp = [i for i in range(0, len(x_label))]
ticks_sp_2 = [x + barWidth for x in ticks_sp]
fig, ax = plt.subplots()
total_received_msg_dht_list = []
total_received_msg_req_dht_list = []
total_received_msg_new_list = []
total_received_msg_req_new_list = []
total_dht = []
total_new = []
for size in x_label:
    list_of_nodes = [x for x in dict_nb_messages[filename].keys()]

    msg_dht = sum([dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['received_msg'] for x in list_of_nodes])
    msg_dht_req = sum([dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['received_msg_req'] for x in list_of_nodes])
    msg_new = sum([dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['received_msg'] for x in list_of_nodes])
    msg_new_req = sum([dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['received_msg_req'] for x in list_of_nodes])

    print("msg_dht : {}".format(msg_dht))
    print("msg_dht_req : {}".format(msg_dht_req))
    print("msg_new : {}".format(msg_new))
    print("msg_new_req : {}".format(msg_new_req))

    total_received_msg_dht_list.append(msg_dht)
    total_received_msg_req_dht_list.append(msg_dht_req)
    total_received_msg_new_list.append(msg_new)
    total_received_msg_req_new_list.append(msg_new_req)

    tot_dht = msg_dht + msg_dht_req
    tot_new = msg_new + msg_new_req
    total_dht.append(tot_dht)
    total_new.append(tot_new)
    print("TOTAL DHT : {}".format(tot_dht))
    print("TOTAL NEW : {}".format(tot_new))
    increase = (float(msg_new) - float(tot_dht)) / float (tot_dht)
    print(round(increase*100,1))


ax.bar(ticks_sp, total_received_msg_dht_list, width=barWidth, label='DHT-Updates')
ax.bar(ticks_sp, total_received_msg_req_dht_list, width=barWidth, bottom=total_received_msg_dht_list, label='DHT-requests', color='red')
for i in range(len(total_dht)):
    ax.text(ticks_sp[i] - (barWidth/float(8)), total_dht[i] + 200, str(total_dht[i]),fontweight='bold')

ax.bar(ticks_sp_2, total_received_msg_new_list, width=barWidth, label='New-Updates')
ax.bar(ticks_sp_2, total_received_msg_req_new_list, width=barWidth, bottom=total_received_msg_new_list, label='New-requests', color='red')
for i in range(len(total_new)):
    ax.text(ticks_sp_2[i] - (barWidth/float(8)), total_new[i] + 200, str(total_new[i]),fontweight='bold')


plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
axes = plt.gca()
axes.yaxis.grid()
max_value = max(max(total_dht), max(total_new))
plt.ylim(bottom=0, top=max_value+5000)
ax.legend()
plt.xlabel("Size of cache")
plt.ylabel("Total number of messages")
plt.title("Impact of cache size on the number of messages")
plt.show()


for size in cache_sizes:
    list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
    x_label = list(range(1, len(dict_nb_messages[filename]) + 1, 1))
    y_dht = [dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['received_msg'] + dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['received_msg_req'] for x in list_of_nodes]
    y_aaa = [dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['received_msg'] + dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['received_msg_req']for x in list_of_nodes]

    dht_average = mean(y_dht)
    aaa_average = mean(y_aaa)
    print("Cache {} - Number of received messages:".format(size))
    print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
    print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))

    # set width of bar
    barWidth = 0.35

    # Set position of bar on X axis
    ticks_sp = [i for i in range(0, len(list_of_nodes))]
    ticks_sp_2 = [x + barWidth for x in ticks_sp]
    fig, ax = plt.subplots()

    ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b')
    ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')

    plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
    plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
    axes = plt.gca()
    axes.yaxis.grid()
    ax.legend()
    plt.tight_layout()
    plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
    plt.xlabel("Node identifier")
    plt.ylabel("Number of received messages")
    plt.title(
        "Distribution of the number of received messages for each node of the infrastructure - Cache size = {}".format(
            size))
    plt.show()

    # Sent_msg
    list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
    x_label = list(range(1, len(dict_nb_messages[filename]) + 1, 1))
    y_dht = [len(dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['sent_msg']) + dict_nb_messages["dht-{}-{}".format(size, update_interval)][x][
        'sent_req'] for x in list_of_nodes]
    y_aaa = [len(dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['sent_msg']) for x in list_of_nodes]

    dht_average = mean(y_dht)
    aaa_average = mean(y_aaa)

    print("Cache {} - Number of sent messages:".format(size))
    print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
    print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))

    # set width of bar
    barWidth = 0.35

    # Set position of bar on X axis
    ticks_sp = [i for i in range(0, len(list_of_nodes))]
    ticks_sp_2 = [x + barWidth for x in ticks_sp]
    fig, ax = plt.subplots()

    ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b')
    ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')

    plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
    plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
    axes = plt.gca()
    axes.yaxis.grid()
    ax.legend()
    plt.tight_layout()
    plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
    plt.xlabel("Node identifier")
    plt.ylabel("Number of sent messages")
    plt.title(
        "Distribution of the number of sent messages for each node of the infrastructure - Cache size = {}".format(
            size))
    plt.show()

    # Number of messages in list
    list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
    x_label = list(range(1, len(dict_nb_messages[filename]) + 1, 1))
    y_dht = [mean(dict_nb_messages["dht-{}-{}".format(size, update_interval)][x]['sent_msg']) for x in list_of_nodes]
    y_aaa = [mean(dict_nb_messages["new-{}-{}".format(size, update_interval)][x]['sent_msg']) for x in list_of_nodes]

    dht_average = mean(y_dht)
    aaa_average = mean(y_aaa)

    print("Cache {} - Number of messages in an IP packet:".format(size))
    print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
    print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))

    # set width of bar
    barWidth = 0.35

    # Set position of bar on X axis
    ticks_sp = [i for i in range(0, len(list_of_nodes))]
    ticks_sp_2 = [x + barWidth for x in ticks_sp]
    fig, ax = plt.subplots()

    ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b')
    ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')

    plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
    plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
    axes = plt.gca()
    axes.yaxis.grid()
    ax.legend()
    plt.tight_layout()
    plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
    plt.xlabel("Node identifier")
    plt.ylabel("Number of messages in the IP packet")
    plt.title(
        "Distribution of the number of messages in the IP packet for each node of the infrastructure - Cache size = {}".format(
            size))
    plt.show()
# import os
# import matplotlib.pyplot as plt
# from statistics import mean, stdev, pstdev
#
# path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_5s/Renater20000Jobs_Cache20_40_60_seed777_5s/transient"
# # Get nbr of messages of AAA algo:
# os.chdir(path)
# list_of_files = [x for x in os.listdir(os.getcwd())]
# list_of_xps = [x for x in list_of_files if x.startswith("new") or x.startswith("dht")]
# cache_sizes = set([x.split("-")[1] for x in list_of_xps])
# dict_nb_messages = {}
# results = {}
# already_done = set()
# for filename in list_of_xps:
# 	print(filename)
# 	os.chdir(path + "/" + filename+"/")
# 	if filename not in dict_nb_messages: dict_nb_messages.update({filename: {}})
# 	for node in os.listdir(os.getcwd()):
# 		os.chdir(path + "/" + filename+"/"+node+ "/root/deploy/traces")
# 		if os.path.exists("_node_stderr.txt"):
# 			if filename.startswith("new"):
# 				cmd = """ grep "Nb of JSON" _node_stderr.txt | wc -l """
# 			elif filename.startswith("dht"):
# 				cmd = """ grep "HANDLE DHT:START" _node_stderr.txt | wc -l """
# 			nbr_messages = int(os.popen(cmd).read())
# 			dict_nb_messages[filename].update({node: {'received_msg': nbr_messages, 'sent_msg': []}})
#
# 			cmd = """ grep "nb_of_msgs:" _node_stderr.txt """
# 			sent_msg = os.popen(cmd).read()
# 			sent_msg_splitted = sent_msg.split('\n')
# 			del sent_msg_splitted[-1]
# 			for entry in sent_msg_splitted:
# 				nbr_sent_messages = entry.split(':')[8].split("-")[0]
# 				dict_nb_messages[filename][node]['sent_msg'].append(int(nbr_sent_messages))
#
# for size in cache_sizes:
#
# 	list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
# 	x_label = list(range(1, len(dict_nb_messages[filename])+1, 1))
# 	y_dht = [dict_nb_messages["dht-{}".format(size)][x]['received_msg'] for x in list_of_nodes]
# 	y_aaa = [dict_nb_messages["new-{}".format(size)][x]['received_msg'] for x in list_of_nodes]
#
# 	dht_average = mean(y_dht)
# 	aaa_average = mean (y_aaa)
# 	print("Cache {} - Number of received messages:".format(size))
# 	print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
# 	print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))
#
# 	# set width of bar
# 	barWidth = 0.35
#
# 	# Set position of bar on X axis
# 	ticks_sp = [i for i in range(0,len(list_of_nodes))]
# 	ticks_sp_2 = [x + barWidth for x in ticks_sp]
# 	fig, ax = plt.subplots()
#
# 	ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b' )
# 	ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')
#
# 	plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
# 	plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
# 	axes = plt.gca()
# 	axes.yaxis.grid()
# 	ax.legend()
# 	plt.tight_layout()
# 	plt.xticks([r + barWidth/2 for r in range(len(ticks_sp))], x_label)
# 	plt.xlabel("Node identifier")
# 	plt.ylabel("Number of received messages")
# 	plt.title("Distribution of the number of received messages for each node of the infrastructure - Cache size = {}".format(size))
# 	plt.show()
#
# 	# Sent_msg
# 	list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
# 	x_label = list(range(1, len(dict_nb_messages[filename]) + 1, 1))
# 	y_dht = [len(dict_nb_messages["dht-{}".format(size)][x]['sent_msg']) for x in list_of_nodes]
# 	y_aaa = [len(dict_nb_messages["new-{}".format(size)][x]['sent_msg']) for x in list_of_nodes]
#
# 	dht_average = mean(y_dht)
# 	aaa_average = mean(y_aaa)
#
# 	print("Cache {} - Number of sent messages:".format(size))
# 	print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
# 	print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))
#
# 	# set width of bar
# 	barWidth = 0.35
#
# 	# Set position of bar on X axis
# 	ticks_sp = [i for i in range(0, len(list_of_nodes))]
# 	ticks_sp_2 = [x + barWidth for x in ticks_sp]
# 	fig, ax = plt.subplots()
#
# 	ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b')
# 	ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')
#
# 	plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
# 	plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
# 	axes = plt.gca()
# 	axes.yaxis.grid()
# 	ax.legend()
# 	plt.tight_layout()
# 	plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
# 	plt.xlabel("Node identifier")
# 	plt.ylabel("Number of sent messages")
# 	plt.title(
# 		"Distribution of the number of sent messages for each node of the infrastructure - Cache size = {}".format(
# 			size))
# 	plt.show()
#
# 	# Number of messages in list
# 	list_of_nodes = [x for x in dict_nb_messages[filename].keys()]
# 	x_label = list(range(1, len(dict_nb_messages[filename]) + 1, 1))
# 	y_dht = [mean(dict_nb_messages["dht-{}".format(size)][x]['sent_msg']) for x in list_of_nodes]
# 	y_aaa = [mean(dict_nb_messages["new-{}".format(size)][x]['sent_msg']) for x in list_of_nodes]
#
# 	dht_average = mean(y_dht)
# 	aaa_average = mean(y_aaa)
#
# 	print("Cache {} - Number of messages in an IP packet:".format(size))
# 	print("DHT mean: {} - std: {}".format(str(dht_average), pstdev(y_dht)))
# 	print("AAA mean: {} - std: {}".format(str(aaa_average), pstdev(y_aaa)))
#
# 	# set width of bar
# 	barWidth = 0.35
#
# 	# Set position of bar on X axis
# 	ticks_sp = [i for i in range(0, len(list_of_nodes))]
# 	ticks_sp_2 = [x + barWidth for x in ticks_sp]
# 	fig, ax = plt.subplots()
#
# 	ax.bar(ticks_sp, y_aaa, width=barWidth, label='AAA', color='b')
# 	ax.bar(ticks_sp_2, y_dht, width=barWidth, label='DHT', color='r')
#
# 	plt.axhline(y=dht_average, color='r', linestyle='--', label='DHT average')
# 	plt.axhline(y=aaa_average, color='b', linestyle='--', label='AAA average')
# 	axes = plt.gca()
# 	axes.yaxis.grid()
# 	ax.legend()
# 	plt.tight_layout()
# 	plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_label)
# 	plt.xlabel("Node identifier")
# 	plt.ylabel("Number of messages in the IP packet")
# 	plt.title(
# 		"Distribution of the number of messages in the IP packet for each node of the infrastructure - Cache size = {}".format(
# 			size))
# 	plt.show()
