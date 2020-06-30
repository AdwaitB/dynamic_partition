import matplotlib.pyplot as plt
import numpy as np
import csv
import os
import statistics
from cons import MAX_NUMBER_JOBS

# Read each experiment csv log and put all the download times in a list
path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_10s/Renater20000Jobs_Cache20_40_60_seed777_10s/transient"
os.chdir(path)
cmd = """ find  ./* -name "traces_*.csv" """
data_path = os.popen(cmd).read()
data_path = data_path.split("\n")
data_path = [x for x in data_path if "small" not in x and x != """"""""]
counter = 0
for csv_file in data_path:
    download_times = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line with names of columns
        for row in reader:
            if counter < MAX_NUMBER_JOBS:
                download_times.append(float(row[9]))
                counter += 1
    num_bins = 10000
    counts, bin_edges = np.histogram(download_times, bins=num_bins, normed=True)
    cdf = np.cumsum(counts)
    label = csv_file.split("_")[1].split(".")[0]
    if label.startswith("dht"): linestyle, width = "--", 2
    elif label.startswith("new"): linestyle, width = "-.", 2
    elif label.startswith("baseline"): linestyle, width = "-", 2
    plt.plot(bin_edges[1:], cdf / cdf[-1], label=label, linestyle=linestyle, linewidth=width)
    print("mean "+csv_file.split("_")[1].split(".")[0] + ": "+ str(statistics.mean(download_times)))
    counter = 0

# Plot the CDF
axes = plt.gca()
axes.set_ylim([0, 1])
axes.set_xlim([0, 2.5])
axes = plt.gca()
axes.yaxis.grid()
plt.yticks(np.arange(0, 1.1, 0.1))
plt.legend()
plt.xlabel("Total Time to download the object (seconds) - Including requesting time")
plt.ylabel("CDF")
plt.title("Comparison of objects downloading times between AAA and DHT")
plt.show()