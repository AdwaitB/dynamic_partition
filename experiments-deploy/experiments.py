#!/Users/avankemp/Workspace/Geo-Tables/AdwaitCode/venv/bin/python

import logging
from pprint import pprint as pp

from enoslib.task import enostask
from infra import *
from parse_gml import generate_dict_from_yml
from playbook import *
from post_processing import *
from provider_proxy import *
from utils_xp import *
import os

logging.basicConfig(level=logging.DEBUG)

#infra_current = generate_dict_from_yml("Topologies/condensed_west_europe-inferred.gml")
infra_current = generate_dict_from_yml("Topologies/condensed_west_europe-inferred.gml")
# infra_current = INFRA_complete_10
#infra_current = INFRA_triangle
#provider = Providers.Vagrant
provider = Providers.G5K
cache_size_list = [20, 40, 60]
interval_list =  [0.001, 1, 2, 3, 4, 5]
#interval_list =  [1]
pp(infra_current)


@enostask(new=True)
def deploy(env=None):
	p = ProviderProxy(provider, infra_current)
	roles, networks = p.deploy_infra(infra_current)
	play = PlayBook(roles, networks, infra_current)

	print(roles)

	env["p"] = p
	env["roles"], env["networks"] = roles, networks
	env["play"] = play

	if provider == Providers.G5K:
		return p.p.job_id
	else:
		return -1


@enostask()
def emulate(env=None):
	p = env["p"]

	keep_alive = 0

	if provider == Providers.G5K:
		keep_alive = OarKeepAlive(p.p.job_id, g5k_loc)
		keep_alive.start()

	p.emulate()

	if provider == Providers.G5K:
		keep_alive.ongoing = False
		keep_alive.join()


@enostask()
def destroy(env=None):
	p = env["p"]
	p.destroy_provider()
	cleanup()


@enostask()
def run_exp(iteration, env=None):
	play = env["play"]
	play.initialize_files()
	play.start_services(iteration)


@enostask()
def fetch(setting, env=None):
	play = env["play"]
	play.fetch(setting)


def experiments(setting, destroy_enable, first_deploy=True):
	if first_deploy:
		job_id = deploy()

		keep_alive = 0

		if provider == Providers.G5K:
			keep_alive = OarKeepAlive(job_id, g5k_loc)
			keep_alive.start()
		emulate()

	run_exp(setting)
	fetch(setting)

	if provider == Providers.G5K:
		keep_alive.ongoing = False
		keep_alive.join()

	if destroy_enable:
		destroy()

	#cleanup()

def set_cache_size(new_cache_size):
	cmd = """ grep "MAX_CACHE_SIZE =" ../ipfs-table-update-backend/constants.py  """
	old_cache = os.popen(cmd).read()
	fin = open("../ipfs-table-update-backend/constants.py", "rt")
	data = fin.read()
	data = data.replace(old_cache, "MAX_CACHE_SIZE = {}\n".format(new_cache_size))
	fin.close()
	fin = open("../ipfs-table-update-backend/constants.py", "wt")
	fin.write(data)
	fin.close()


def set_update_interval(new_interval):
    cmd = """ grep "UPDATE_INTERVAL =" ../ipfs-table-update-backend/node_handler.py  """
    old_interval = os.popen(cmd).read()
    fin = open("../ipfs-table-update-backend/node_handler.py", "rt")
    data = fin.read()
    data = data.replace(old_interval, "UPDATE_INTERVAL = {}\n".format(new_interval))
    fin.close()
    fin = open("../ipfs-table-update-backend/node_handler.py", "wt")
    fin.write(data)
    fin.close()

def main():
	os.system('rm -rf current enos_*')  # Clean the previous enoslib related folders.
    experiments("baseline", False, first_deploy=True)
    for interval in interval_list:
        set_update_interval(interval)
        for cache_size in cache_size_list:
            set_cache_size(cache_size)
            experiments("dht-{}-{}s".format(cache_size, interval), False, first_deploy=False)
            experiments("new-{}-{}s".format(cache_size, interval), False, first_deploy=False)

time_start = time.time()
main()
# plot_complete()
for cache_size in cache_size_list:
	merge_traces(cache_size)
destroy()
print("Total Time: " + str(time.time() - time_start))
