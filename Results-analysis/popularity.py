import csv
import matplotlib.pyplot as plt
from statistics import mean
import os

# Read each experiment csv log and put all data into a dict
MAX_SEQ_NUMBER = 40 # Significative value of the number of time a given filehash has been requested.
                    # After 40, not enough data to plot meaningful average value

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/JOBS_50ms/Renater20000Jobs_Cache20_40_60_seed777_3s/transient"
os.chdir(path)
cmd = """ find  ./* -name "traces_*.csv" """
data_path = os.popen(cmd).read()
data_path = data_path.split("\n")
data_path = [x for x in data_path if "small" not in x and x != """"""""]
dict_download_time = {}
mapping_hash_sizes = {}
mean_download_time_per_sequence_number = {}
for csv_file in data_path:
    trace_name = csv_file.split("_")[1].split(".")[0]
    dict_download_time[trace_name] = {}
    mean_download_time_per_sequence_number[trace_name] = {}
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line with names of columns
        for row in reader:
            file_hash = float(row[2])
            size = float(row[6])
            if size not in mapping_hash_sizes:
                mapping_hash_sizes[size] = set()
            mapping_hash_sizes[size].add(file_hash)
            if file_hash not in dict_download_time[trace_name]:
                dict_download_time[trace_name][file_hash] = {'req': [], 'download': [], 'total': []}
            dict_download_time[trace_name][file_hash]['download'].append(float(row[7]))
            dict_download_time[trace_name][file_hash]['req'].append(float(row[8]))
            dict_download_time[trace_name][file_hash]['total'].append(float(row[9]))

for csv_file in data_path:
    trace_name = csv_file.split("_")[1].split(".")[0]
    for size in mapping_hash_sizes:
        if size not in mean_download_time_per_sequence_number[trace_name]:
            mean_download_time_per_sequence_number[trace_name][size] = {}
        for file_hash in mapping_hash_sizes[size]:
            number_of_time_requested = len(dict_download_time[trace_name][file_hash]['download'])
            for i in range(number_of_time_requested):
                if i not in mean_download_time_per_sequence_number[trace_name][size]:
                    mean_download_time_per_sequence_number[trace_name][size][i] = []
                mean_download_time_per_sequence_number[trace_name][size][i].append(dict_download_time[trace_name][file_hash]['download'][i])

list_of_file_sizes_sorted = sorted(list(mapping_hash_sizes.keys()))
cache_sizes = ['1KB', '32K', '64KB', '256KB', '512KB', '1MB', '2MB', '16MB', '32MB']
index=0
for size in list_of_file_sizes_sorted:
    for csv_file in data_path:
        trace_name = csv_file.split("_")[1].split(".")[0]
        average_download_times_to_plot = []
        for i in range(0,MAX_SEQ_NUMBER):
            average_download_times_to_plot.append(mean(mean_download_time_per_sequence_number[trace_name][size][i]))
        plt.xticks(range(1,MAX_SEQ_NUMBER+1, 1))
        label= trace_name
        if label.startswith("dht"): linestyle, width = "--", 2
        elif label.startswith("new"): linestyle, width = "-.", 2
        elif label.startswith("baseline"): linestyle, width = "-", 2
        plt.plot(range(1,MAX_SEQ_NUMBER+1), average_download_times_to_plot, label=label, linestyle=linestyle, linewidth=width)

    plt.title("Impact of file popularity - Average download time (s) depending on the sequence number \n (Requesting time is "
    "*not* included here) - Object size = {}".format(cache_sizes[index]))
    index += 1
    plt.legend()

    plt.xlabel("Number of time a given object has been requested in the system")
    plt.ylabel("Average download time (seconds)")
    plt.ylim(bottom=0)
    plt.show()




# path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater20000Jobs_100ms/transient"
# input_data = path + "/traces.csv"
#
# set_file_sizes = set([1048.576, 4194.304, 262.144, 32.768, 524.288, 131.072, 4.096, 8388.608, 2097.152])
# dict_download_time = {}
#
# with open(input_data, 'r') as file:
#     reader = csv.reader(file)
#     next(reader)  # Skip the first line with names of columns
#     for row in reader:
#         file_hash = float(row[3])
#         file_size = float(row[7])
#
#         time_download_dht = float(row[8])
#         time_request_dht = float(row[9])
#         time_total_dht = float(row[10])
#
#         time_download_aaa = float(row[17])
#         time_request_aaa = float(row[18])
#         time_total_aaa = float(row[19])
#
#         if file_hash not in dict_download_time:
#             dict_download_time.update({file_hash: {'file_size': file_size, 'time_download_dht': [],
#                                                    'time_request_dht': [], 'time_total_dht': [],
#                                                    'time_download_aaa': [], 'time_request_aaa': [],
#                                                    'time_total_aaa': []}})
#
#         dict_download_time[file_hash]['time_download_dht'].append(time_download_dht)
#         dict_download_time[file_hash]['time_request_dht'].append(time_request_dht)
#         dict_download_time[file_hash]['time_total_dht'].append(time_total_dht)
#
#         dict_download_time[file_hash]['time_download_aaa'].append(time_download_aaa)
#         dict_download_time[file_hash]['time_request_aaa'].append(time_request_aaa)
#         dict_download_time[file_hash]['time_total_aaa'].append(time_total_aaa)
#
# objects_per_sizes = {}
# for file_size in set_file_sizes:
#     objects_per_sizes.update({file_size: []})
#
# for entry in dict_download_time:
#     objects_per_sizes[dict_download_time[entry]["file_size"]].append(dict_download_time[entry])
#
# to_plot = 'aaa'
# time_to_plot = 'time_download_{}'.format(to_plot)
#
# max_length = 0
# for file_size in set_file_sizes:
#     for entry in objects_per_sizes[file_size]:
#         length = len(entry[time_to_plot])
#         if length > max_length:
#             max_length = length
#
# list_of_file_sizes_sorted = sorted(list(set_file_sizes))
# list_to_plot_aaa = []
# list_x_axis_aaa = []
#
# for file_size in list_of_file_sizes_sorted:
#     list_of_time_by_sequence_aaa = []
#     for i in range(max_length): list_of_time_by_sequence_aaa.append([])
#     for entry in objects_per_sizes[file_size]:
#         for i in range(len(entry[time_to_plot])):
#             list_of_time_by_sequence_aaa[i].append(entry[time_to_plot][i])
#
#     list_of_mean_aaa = []
#     for times in list_of_time_by_sequence_aaa:
#         if len(times) > 0: list_of_mean_aaa.append(mean(times))
#
#     x_ticks_aaa = list(range(0, len(list_of_mean_aaa)))
#     y_data_aaa = list_of_mean_aaa
#
#     list_x_axis_aaa.append(x_ticks_aaa)
#     list_to_plot_aaa.append(y_data_aaa)
#
# to_plot = 'dht'
# time_to_plot = 'time_download_{}'.format(to_plot)
#
# max_length = 0
# for file_size in set_file_sizes:
#     for entry in objects_per_sizes[file_size]:
#         length = len(entry[time_to_plot])
#         if length > max_length:
#             max_length = length
#
# list_of_file_sizes_sorted = sorted(list(set_file_sizes))
# list_to_plot_dht = []
# list_x_axis_dht = []
#
# for file_size in list_of_file_sizes_sorted:
#     list_of_time_by_sequence_dht = []
#     for i in range(max_length): list_of_time_by_sequence_dht.append([])
#     for entry in objects_per_sizes[file_size]:
#         for i in range(len(entry[time_to_plot])):
#             list_of_time_by_sequence_dht[i].append(entry[time_to_plot][i])
#
#     list_of_mean_dht = []
#     for times in list_of_time_by_sequence_dht:
#         if len(times) > 0: list_of_mean_dht.append(mean(times))
#
#     x_ticks_dht = list(range(0, len(list_of_mean_dht)))
#     y_data_dht = list_of_mean_dht
#
#     list_x_axis_dht.append(x_ticks_dht)
#     list_to_plot_dht.append(y_data_dht)
#
# x_labels = ["1KB", "8KB", "32KB", "64KB", "128KB", "256KB", "512KB", "1MB", "2MB"]
# # # To plot the first 4 graphs (4KB, 64KB, 256KB, 512KB)
# fig, ax = plt.subplots(2, 2)
# ax[0, 0].plot(list_x_axis_aaa[0], list_to_plot_aaa[0])
# ax[0, 0].plot(list_x_axis_dht[0], list_to_plot_dht[0])
# ax[0, 0].legend(["1 KB - AAA", "1 KB - DHT"])
# ax[0, 0].set_ylim(bottom=0)
# ax[0, 1].plot(list_x_axis_aaa[1], list_to_plot_aaa[1])
# ax[0, 1].plot(list_x_axis_dht[1], list_to_plot_dht[1])
# ax[0, 1].legend(["8 KB - AAA", "8 KB - DHT"])
# ax[0, 1].set_ylim(bottom=0)
# ax[1, 0].plot(list_x_axis_aaa[2], list_to_plot_aaa[2])
# ax[1, 0].plot(list_x_axis_dht[2], list_to_plot_dht[2])
# ax[1, 0].legend(["32 KB - AAA", "32 KB - DHT"])
# ax[1, 0].set_ylim(bottom=0)
# ax[1, 1].plot(list_x_axis_aaa[3], list_to_plot_aaa[3])
# ax[1, 1].plot(list_x_axis_dht[3], list_to_plot_dht[3])
# ax[1, 1].legend(["64 KB - AAA", "64 KB - DHT"])
# ax[1, 1].set_ylim(bottom=0)
#
# plt.suptitle(
#     "Impact of file popularity - Average download time (s) depending on the sequence number \n (Requesting time is "
#     "*not* included here)",
#     fontsize=14)
# plt.show()
#
# # # To plot the following 4 graphs (1MB, 8MB, 32MB, 64MB)
# fig, ax = plt.subplots(2, 2)
# ax[0, 0].plot(list_x_axis_aaa[4], list_to_plot_aaa[4])
# ax[0, 0].plot(list_x_axis_dht[4], list_to_plot_dht[4])
# ax[0, 0].legend(["128 KB - AAA", "128 KB - DHT"])
# ax[0, 0].set_ylim(bottom=0)
# ax[0, 1].plot(list_x_axis_aaa[5], list_to_plot_aaa[5])
# ax[0, 1].plot(list_x_axis_dht[5], list_to_plot_dht[5])
# ax[0, 1].legend(["256 KB - AAA", "256 KB - DHT"])
# ax[0, 1].set_ylim(bottom=0)
# ax[1, 0].plot(list_x_axis_aaa[6], list_to_plot_aaa[6])
# ax[1, 0].plot(list_x_axis_dht[6], list_to_plot_dht[6])
# ax[1, 0].legend(["512 KB - AAA", "512 KB - DHT"])
# ax[1, 0].set_ylim(bottom=0)
# ax[1, 1].plot(list_x_axis_aaa[7], list_to_plot_aaa[7])
# ax[1, 1].plot(list_x_axis_dht[7], list_to_plot_dht[7])
# ax[1, 1].legend(["1 MB - AAA", "1 MB- DHT"])
# ax[1, 1].set_ylim(bottom=0)
#
# plt.suptitle(
#     "Impact of file popularity - Average download time (s) depending on the sequence number \n (Requesting time is "
#     "*not* included here)",
#     fontsize=14)
# plt.show()
#
# # # [4.096, 65.536, 262.144, 524.288, 1048.576, 8388.608, 33554.432, 67108.864, 134217.728]
# # # # To plot 8 graphs
# # fig, ax = plt.subplots(4, 2)
# # ax[0, 0].plot(list_x_axis[0], list_to_plot[0], label='4KB')
# # ax[0, 0].legend(["4 KB"])
# # ax[0, 1].plot(list_x_axis[1], list_to_plot[1], label='64KB')
# # ax[0, 1].legend(["64 KB"])
# # ax[1, 0].plot(list_x_axis[2], list_to_plot[2], label='265KB')
# # ax[1, 0].legend(["256 KB"])
# # ax[1, 1].plot(list_x_axis[3], list_to_plot[3], label='512KB')
# # ax[1, 1].legend(["512 KB"])
# # ax[2, 0].plot(list_x_axis[4], list_to_plot[4], label='1MB')
# # ax[2, 0].legend(["1 MB"])
# # ax[2, 1].plot(list_x_axis[5], list_to_plot[5], label='8MB')
# # ax[2, 1].legend(["8 MB"])
# # ax[3, 0].plot(list_x_axis[6], list_to_plot[6], label='32MB')
# # ax[3, 0].legend(["32 MB"])
# # ax[3, 1].plot(list_x_axis[7], list_to_plot[7], label='64MB')
# # ax[3, 1].legend(["64 MB"])
# #
# # plt.suptitle("Impact of file popularity - Average download time (s) depending on the sequence number.", fontsize=14)
# # plt.show()
