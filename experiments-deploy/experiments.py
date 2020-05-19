#!/Users/avankemp/Workspace/Geo-Tables/AdwaitCode/venv/bin/python

import logging
from pprint import pprint as pp

from enoslib.task import enostask
from infra import *
from parse_gml import generate_dict_from_yml
from playbook import *
from post_processing import *
from provider_proxy import *
from utils import *

logging.basicConfig(level=logging.DEBUG)

infra_current = generate_dict_from_yml("Topologies/Renater2010.gml")
# infra_current = INFRA_complete_10
# infra_current = INFRA_two
# provider = Providers.Vagrant
provider = Providers.G5K

pp(infra_current)


@enostask(new=True)
def deploy(env=None):
	p = ProviderProxy(provider, infra_current)
	roles, networks = p.deploy_infra()
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


def experiments(setting, destroy_enable):
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


def main():
	if provider == Providers.G5K:
		# destroy()
		experiments("new", False)
		experiments("dht", False)
		# destroy()
	elif provider == Providers.Vagrant:
		# destroy()
		experiments("dht", True)
		experiments("new", False)
		# destroy()


time_start = time.time()
main()
# plot_complete()
merge_traces()
destroy()
print("Total Time: " + str(time.time() - time_start))
