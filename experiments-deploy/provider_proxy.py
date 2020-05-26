from enum import Enum

from enoslib.api import emulate_network, discover_networks
from g5k_config import *
from infra_parser_xp import *
from vagrant_config import *


class ProviderProxy:
	def __init__(self, provider, infra, image=""):
		if provider == Providers.Vagrant:
			if image == "":
				self.p = VagrantProvider(infra)
			else:
				self.p = VagrantProvider(infra, image)
		elif provider == Providers.G5K:
			if image == "":
				self.p = G5KProvider(infra)
			else:
				self.p = G5KProvider(infra, image)
		else:
			assert False

		self.infra = infra

		self.roles, self.networks = [0, 0]

	def deploy_infra(self):
		self.roles, self.networks = self.p.deploy_infra()

		# Ifconfig and parse
		discover_networks(self.roles, self.networks)

		return self.roles, self.networks

	def emulate(self):
		# Now emulate the network latencies
		pp(self.infra)
		emulation_conf = self.create_emulation_configuration(self.infra)

		if emulation_conf is not None:
			# reset_network(roles=self.roles)
			emulate_network(emulation_conf, roles=self.roles)
			# validate_network(roles=self.roles)

	@staticmethod
	def create_emulation_configuration(infra):
		infra_parsed = Infra(infra)

		top = infra_parsed.shortest_path_dist

		# Building the network constraints
		emulation_conf = {
			"enable": True,
			"default_delay": "0ms",
			"default_rate": "1gbit",
			"groups": list(infra.keys())
		}

		# Building the specific constraints
		constraints = []
		for node in infra:
			for other_node in infra:
				if other_node == "master" or node == "master" or other_node == node:
					constraints.append({
						"src": node,
						"dst": other_node,
						"delay": "0ms",
						"symetric": False
					})
					continue

				constraints.append({
					"src": node,
					"dst": other_node,
					"delay": str(top[node][other_node]) + "ms",
					"symetric": False
				})

		if len(constraints) == 0:
			return None

		emulation_conf["constraints"] = constraints

		pp(emulation_conf)

		return emulation_conf

	def destroy_provider(self):
		self.p.destroy()


class Providers(Enum):
	Vagrant = 0
	G5K = 1
