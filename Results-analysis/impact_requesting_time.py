from matplotlib import pyplot as plt
import pandas as pd
import os
import csv
from statistics import mean

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater20000Jobs_100ms/transient"
os.chdir(path)
cmd = """ find  ./* -name "traces_*.csv" """
data_path = os.popen(cmd).read()
data_path = data_path.split("\n")
data_path = [x for x in data_path if "small" not in x and x != """"""""]
dict_download_time = {}
for csv_file in data_path:
    trace_name = csv_file.split("_")[1].split(".")[0]
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line with names of columns
        for row in reader:
            file_hash = float(row[2])
            size = float(row[6])
            if trace_name not in dict_download_time:
                dict_download_time[trace_name] = {}
            if size not in dict_download_time[trace_name]:
                dict_download_time[trace_name][size] = {'req': [], 'download': [], 'total': []}
            dict_download_time[trace_name][size]['download'].append(float(row[7]))
            dict_download_time[trace_name][size]['req'].append(float(row[8]))
            dict_download_time[trace_name][size]['total'].append(float(row[9]))


# set width of bar
barWidth = 0.1
ticks_sp = [i for i in range(0, len(dict_download_time[trace_name].keys()))]
fig, ax = plt.subplots()
width = 0.15
i = 1

for trace in sorted(list(dict_download_time.keys()))[::-1]:
    sizes = sorted(list(dict_download_time[trace_name].keys()))
    average_download_time = []
    average_request_time = []
    for size in sizes:
        average_download_time.append(mean(dict_download_time[trace][size]['download']))
        average_request_time.append(mean(dict_download_time[trace][size]['req']))
    if "new" in trace: x_ticks = [x + i*barWidth for x in ticks_sp]
    elif "dht" in trace: x_ticks = [x + (i+0.4)*barWidth for x in ticks_sp]
    elif "baseline" in trace: x_ticks = [x + (i+0.8)*barWidth for x in ticks_sp]
    ax.bar(x_ticks, average_request_time, width=barWidth, label='Request {}'.format(trace), color='red', edgecolor='black', hatch='//')
    ax.bar(x_ticks, average_download_time, width=barWidth, bottom=average_request_time, label='Download {}'.format(trace), edgecolor='black')
    ax.legend()
    i += 1

x_labels = ["1KB", "8KB", "32KB", "64KB", "128KB", "256KB", "512KB", "1MB", "2MB"]
plt.xticks([r + (barWidth / len(dict_download_time.keys())) + 0.5 for r in range(len(ticks_sp))], x_labels)
axes = plt.gca()
axes.yaxis.grid()
plt.xlabel("Size of Dataset (KB)")
plt.ylabel("Average Time to get an object (s)")
plt.title("Impact of the request time to get an object for DHT and AAA for different cache sizes")
plt.show()

# path = "/Users/avankemp/PycharmProjects/dynamic_partition/experiments-deploy/transient"
# input_data = path + "/traces-20.csv"
#
# ticks = [1, 8, 32, 64, 128, 256, 512, 1024, 2048]
# ticks_scaled = [i * 1 for i in ticks]
#
# data = pd.read_csv(input_data)
#
# x_labels = ["1KB", "8KB", "32KB", "64KB", "128KB", "256KB", "512KB", "1MB", "2MB"]
# # x_labels = ["4KB", "64KB", "256KB", "512KB", "1MB", "8MB", "32MB", "64MB", "128MB"]
#
# print(data.head)
#
# dht_total = data.groupby(["Size (B) DHT"])['Total Time DHT'].mean()
#
# dht_download = data.groupby(["Size (B) DHT"])['Time Download DHT'].mean().reset_index()
# dht_request = data.groupby(["Size (B) DHT"])['Time Request DHT'].mean().reset_index()
#
# new_download = data.groupby(["Size (B) DHT"])['Time Download NEW'].mean().reset_index()
# new_request = data.groupby(["Size (B) DHT"])['Time Request NEW'].mean().reset_index()
#
# print(new_request)
# print(new_download)
#
# print(dht_request)
# print(dht_download)
#
# # set width of bar
# barWidth = 0.25
#
# # Set position of bar on X axis
# ticks_sp = [i for i in range(0, len(ticks_scaled))]
# ticks_sp_2 = [x + barWidth for x in ticks_sp]
#
# fig, ax = plt.subplots()
# width = 0.35
#
# ax.bar(ticks_sp, new_request['Time Request NEW'], width=barWidth, label='Request (AAA)')
# ax.bar(ticks_sp, new_download['Time Download NEW'], width=barWidth, bottom=new_request['Time Request NEW'],
#        label='Download (AAA)', color='skyblue')
#
# ax.bar(ticks_sp_2, dht_request['Time Request DHT'], width=barWidth, label='Request (DHT)', color='red')
# ax.bar(ticks_sp_2, dht_download['Time Download DHT'], width=barWidth, bottom=dht_request['Time Request DHT'],
#        label='Download (DHT)', color='orange')
#
# ax.legend()
#
# plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_labels)
#
# stepsize = 0.10
# start, end = ax.get_ylim()
# # ax.yaxis.set_ticks([x*stepsize for x in range(10*int(start), 10*int(end)+1)])
#
# axes = plt.gca()
# axes.yaxis.grid()
# plt.xlabel("Size of Dataset (KB)")
# plt.ylabel("Average Time to get an object (s)")
# plt.title("Impact of the request time to get an object for DHT and AAA")
#
# plt.show()
#
# time_reduction = []
# for i in range(len(new_download['Time Download NEW'])):
#     total_dht = dht_request['Time Request DHT'][i] + dht_download['Time Download DHT'][i]
#     total_new = new_request['Time Request NEW'][i] + new_download['Time Download NEW'][i]
#     time_reduction.append((total_dht - total_new) * 100 / total_dht)
#
# print(time_reduction)
