from matplotlib import pyplot as plt
from copy import deepcopy as dc
import pandas as pd

# ticks = [1, 16, 64, 128, 256, 2048, 8192, 16384, 32768]
# ticks_scaled = [ i *4 for i in ticks]


path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater20000Jobs_cache10/transient"
input_data = path + "/traces.csv"

ticks = [1, 8, 32, 64, 128, 256, 512, 1024, 2048]
ticks_scaled = [i * 1 for i in ticks]

data = pd.read_csv(input_data)

x_labels = ["1KB", "8KB", "32KB", "64KB", "128KB", "256KB", "512KB", "1MB", "2MB"]
# x_labels = ["4KB", "64KB", "256KB", "512KB", "1MB", "8MB", "32MB", "64MB", "128MB"]

print(data.head)

dht_total = data.groupby(["Size (B) DHT"])['Total Time DHT'].mean()

dht_download = data.groupby(["Size (B) DHT"])['Time Download DHT'].mean().reset_index()
dht_request = data.groupby(["Size (B) DHT"])['Time Request DHT'].mean().reset_index()

new_download = data.groupby(["Size (B) DHT"])['Time Download NEW'].mean().reset_index()
new_request = data.groupby(["Size (B) DHT"])['Time Request NEW'].mean().reset_index()

print(new_request)
print(new_download)

print(dht_request)
print(dht_download)

# set width of bar
barWidth = 0.25

# Set position of bar on X axis
ticks_sp = [i for i in range(0, len(ticks_scaled))]
ticks_sp_2 = [x + barWidth for x in ticks_sp]

fig, ax = plt.subplots()
width = 0.35

ax.bar(ticks_sp, new_request['Time Request NEW'], width=barWidth, label='Request (AAA)')
ax.bar(ticks_sp, new_download['Time Download NEW'], width=barWidth, bottom=new_request['Time Request NEW'],
       label='Download (AAA)', color='skyblue')

ax.bar(ticks_sp_2, dht_request['Time Request DHT'], width=barWidth, label='Request (DHT)', color='red')
ax.bar(ticks_sp_2, dht_download['Time Download DHT'], width=barWidth, bottom=dht_request['Time Request DHT'],
       label='Download (DHT)', color='orange')

ax.legend()

plt.xticks([r + barWidth / 2 for r in range(len(ticks_sp))], x_labels)

stepsize = 0.10
start, end = ax.get_ylim()
# ax.yaxis.set_ticks([x*stepsize for x in range(10*int(start), 10*int(end)+1)])

axes = plt.gca()
axes.yaxis.grid()
plt.xlabel("Size of Dataset (KB)")
plt.ylabel("Average Time to get an object (s)")
plt.title("Impact of the request time to get an object for DHT and AAA")

plt.show()

time_reduction = []
for i in range(len(new_download['Time Download NEW'])):
    total_dht = dht_request['Time Request DHT'][i] + dht_download['Time Download DHT'][i]
    total_new = new_request['Time Request NEW'][i] + new_download['Time Download NEW'][i]
    time_reduction.append((total_dht - total_new) * 100 / total_dht)

print(time_reduction)
