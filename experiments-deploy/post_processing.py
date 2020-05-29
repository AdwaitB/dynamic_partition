from copy import deepcopy as dc
import pandas as pd

from enoslib.task import enostask
from infra_parser_xp import Infra
from matplotlib import pyplot as plt


@enostask()
def merge_traces(env=None):
	alias = Infra.get_alias_by_name(env["roles"], "master")

	csvdht = pd.read_csv("./transient/dht/{}/root/deploy/traces/traces_dht.csv".format(alias))
	csvnew = pd.read_csv("./transient/new/{}/root/deploy/traces/traces_new.csv".format(alias))

	csv = pd.merge(csvdht, csvnew, on='Job ID', suffixes=(' DHT', ' NEW'))
	csv.to_csv("./transient/traces.csv")

	csv = csv[['Size (B) DHT', 'Time Download DHT', 'Time Request DHT', 'Total Time DHT',
			   'Time Download NEW', 'Time Request NEW', 'Total Time NEW']]
	csv.to_csv("./transient/traces_small.csv")


@enostask()
def plot_complete(env=None):
	ticks = [1, 16, 64, 128, 256, 2048, 8192, 16384, 32768]
	ticks_scaled = [i * 4 for i in ticks]
	# ticks = [1, 8, 32, 64, 128, 256, 512, 1024, 2048]
	# ticks_scaled = [i * 1 for i in ticks]
	ticks_sp = [i for i in range(0, len(ticks_scaled))]

	alias = Infra.get_alias_by_name(env["roles"], "master")

	csvdht = pd.read_csv("./transient/dht/{}/root/deploy/traces/traces_dht.csv".format(alias))
	csvnew = pd.read_csv("./transient/new/{}/root/deploy/traces/traces_new.csv".format(alias))

	csvdht = csvdht.groupby(["Size (B)"])['Total Time'].mean().reset_index()  # .apply(lambda x: np.log10(x))
	csvnew = csvnew.groupby(["Size (B)"])['Total Time'].mean().reset_index()  # .apply(lambda x: np.log10(x))

	csvall = dc(csvdht)
	csvall['Total Time NEW'] = csvnew['Total Time']
	csvall['Difference'] = csvall['Total Time'] - csvall['Total Time NEW']
	csvall['Difference Percentage'] = csvall['Difference'] * 100 / csvall['Total Time']

	print(csvall['Difference Percentage'])

	plt.plot(ticks_sp, csvdht['Total Time'], 'r', label='DHT')
	plt.plot(ticks_sp, csvnew['Total Time'], 'b', label='NEW')
	plt.grid(True)

	plt.xticks(ticks_sp, ticks_scaled)
	plt.xlabel("Size of Dataset (KB)")
	plt.legend()
	plt.ylabel("Average Time to Download (s)")
	plt.title("Average time for DHT and NEW")
	plt.savefig("./transient/complete.png")
