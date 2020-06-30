import os
import json
import matplotlib.pyplot as plt


font = {'family': 'normal',
        'size': 30}
plt.rc('font', **font)
plt.rcParams.update({'lines.linewidth': 6, "xtick.labelsize": 30, 'ytick.labelsize': 30})

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/"
os.chdir(path)
with open('best_miss_ration.json') as json_file:
    all_results = json.load(json_file)


cache_sizes = [20, 40, 60]
list_of_interval = list(all_results.keys())
list_of_interval.sort(key=lambda x: float(x.split("_")[5][:-1]))
x_labels = [x.split('_')[5] for x in list_of_interval]

ticks_sp = [i for i in range(0, len(x_labels))]
barWidth = 0.05
i = -len(cache_sizes)

to_plot = {}
for size in cache_sizes:
    j = 0
    to_plot.update({size: {'aaa': [], 'dht': []}})
    for interval in list_of_interval:
        to_plot[size]['aaa'].append(all_results[interval]["new-{}-{}".format(size, x_labels[j])])
        to_plot[size]['dht'].append(all_results[interval]["dht-{}-{}".format(size, x_labels[j])])
        j += 1

    x_ticks = [x + i * barWidth for x in ticks_sp]
    #plt.bar(x_ticks, to_plot[size]['aaa'], label='aaa - {}'.format(size), width=barWidth, edgecolor='black')
    plt.plot(ticks_sp, to_plot[size]['aaa'], label='aaa - {}'.format(size), marker="o", markersize=15)

    i += 1
    x_ticks = [x + i * barWidth for x in ticks_sp]
    #plt.bar(x_ticks, to_plot[size]['dht'], label='dht - {}'.format(size), width=barWidth, hatch='//', edgecolor='black')
    plt.plot(ticks_sp, to_plot[size]['dht'], label='dht - {}'.format(size), marker="x", markersize=15)

    i += 1


#plt.gca().set_yticklabels(['{:.0f}%'.format(x) for x in plt.gca().get_yticks()])
#plt.tight_layout()  # otherwise the right y-label is slightly clipped

plt.legend()
axes = plt.gca()
axes.yaxis.grid()
#plt.gca().set_yticklabels(['{:.0f}%'.format(x) for x in plt.gca().get_yticks()])
plt.gca().set_yticklabels(["0%", "2%", "4%","6%","8%","10%"])
plt.ylim(bottom=0)
# plt.title("Tradeoff between number of exchanged messages and number of 404 errors - {} Jobs".format(NB_JOBS))
plt.xlabel("Update interval (seconds)", fontsize=30)
plt.ylabel("Best-miss ratio (in percent)", fontsize=30)
plt.show()