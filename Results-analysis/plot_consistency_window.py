import os
import json
import matplotlib.pyplot as plt
import pickle
import numpy as np
from matplotlib.pyplot import cm

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater_no_fall_back/"
os.chdir(path)
all_graphs_results = pickle.load(open("dict_consistency_window.p", "rb"))
Nbr_of_intervals = 6

all_list_of_delays = {}

color=iter(cm.rainbow(np.linspace(0,1,Nbr_of_intervals)))
font = {'family': 'normal',
        'size': 30}
plt.rc('font', **font)
plt.rcParams.update({'lines.linewidth': 6, "xtick.labelsize": 30, 'ytick.labelsize': 30})

for interval in all_graphs_results:
    line_color = next(color)
    for filename in all_graphs_results[interval]:
        if "40" in filename:
            list_of_delays = []
            for msg in all_graphs_results[interval][filename]:
                first_send = sorted(all_graphs_results[interval][filename][msg]['sent'])[0]
                last_received = sorted(all_graphs_results[interval][filename][msg]['received'])[-1]
                list_of_delays.append((last_received - first_send).total_seconds())

            sorted_list_of_delays = sorted(list_of_delays)
            all_list_of_delays.update({interval: {filename: sorted_list_of_delays}})
            num_bins = 10000
            counts, bin_edges = np.histogram(sorted_list_of_delays, bins=num_bins, normed=True)
            cdf = np.cumsum(counts)
            if"new" in filename: line = "-"
            elif "dht" in filename: line = "--"
            plt.plot(bin_edges[1:], cdf / cdf[-1], label=filename, linestyle=line, color=line_color)
            plt.legend()

axes = plt.gca()
axes.yaxis.grid()
axes.xaxis.grid()
#plt.gca().set_yticklabels(["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"])
plt.yticks(np.arange(0, 1.1, step=0.1))
plt.xlabel("Maximum message delay (seconds)", fontsize=30)
plt.ylabel("CDF", fontsize=30)
plt.xlim([0, 20])
plt.show()
os.chdir(path)
pickle.dump(all_list_of_delays, open("dict_list_of_delays.p", "wb"))

