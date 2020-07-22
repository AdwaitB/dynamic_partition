import json
from copy import deepcopy as dc
from pprint import pprint as pp
import networkx as nx
import numpy as np
from constants import *


def dict_apply_path(d, l):
	if len(l) == 0:
		return d

	if l[0] not in d:
		d[l[0]] = {}
	return dict_apply_path(d[l[0]], l[1:])


class Infra:
	def __init__(self):
		with open(CONFIG_FOLDER + "infra.json") as json_file:
			infra = json.load(json_file)
			self.infra = infra['infra']
			self.roles = infra['roles']
			self.network = infra['network']

		self.g = self.build_graph()
		self.shortest_path_dist = dict(nx.all_pairs_dijkstra_path_length(self.g))
		self.shortest_paths = dict(nx.all_pairs_dijkstra_path(self.g))
		self.shortest_path_trees = self.build_spt()
		self.shortest_path_trees_deflated = self.build_deflated_spt()

		print("shortest_path_dist")
		#pp(self.shortest_path_dist)
		print("shortest_paths")
		#pp(self.shortest_paths)
		print("shortest_path_trees")
		#pp(self.shortest_path_trees)
		print("shortest_path_trees_deflated")
		#pp(self.shortest_path_trees_deflated)

	def build_graph(self):
		ret = nx.Graph()
		for node in self.infra:
			ret.add_node(self.get_ip_by_name(node))

		for node in self.infra:
			for other_node in self.infra[node]:
				edge_weight = int(self.infra[node][other_node][:-2])
				ret.add_edge(self.get_ip_by_name(node), self.get_ip_by_name(other_node), weight=edge_weight)
		return ret

	def build_spt(self):
		ret = {}
		for origins in self.shortest_paths:
			paths = self.shortest_paths[origins]
			for node in paths:
				dict_apply_path(ret, paths[node])
		return ret

	def build_deflated_spt(self):
		ret = {}
		for origin in self.shortest_path_trees:
			ret[origin] = {}

			# Initialize the lists
			# pprint.pprint(self.shortest_path_trees)
			for node in self.shortest_path_trees:
				ret[origin][node] = []

			active = list()
			active.append({origin: self.shortest_path_trees[origin]})

			while len(active) > 0:
				root = active[0]
				for curr in root:
					active.append(root[curr])
					for node in root[curr]:
						ret[origin][curr].append(node)
				active.pop(0)
		return ret

	def get_name_by_ip(self, ip):
		for role in self.roles:
			if role['extra']['my_subnet_ip'] == ip:
				return role['role']
		return DEFAULT_NODE_NAME

	def get_ip_by_name(self, name):
		for role in self.roles:
			if role['role'] == name:
				return role['address']
		return DEFAULT_IP

	def get_alias_by_ip(self, ip):
		for role in self.roles:
			if role['extra']['my_subnet_ip'] == ip:
				return role['alias']
		return DEFAULT_ALIAS

	def get_ip_by_alias(self, alias):
		for role in self.roles:
			if role['alias'] == alias:
				return role['extra']['my_subnet_ip']
		return DEFAULT_IP

	def get_name_by_alias(self, alias):
		for role in self.roles:
			if role['alias'] == alias:
				return role['role']
		return DEFAULT_NODE_NAME

	def get_alias_by_name(self, name):
		for role in self.roles:
			if role['role'] == name:
				return role['alias']
		return DEFAULT_ALIAS

	def get_name_alias_by_ip(self, ip):
		for role in self.roles:
			if role['extra']['my_subnet_ip'] == ip:
				return role['role'], role['alias']
		return DEFAULT_NODE_NAME, DEFAULT_ALIAS

	def get_spt_neighbours(self, source_ip, node_ip):
		return dc(self.shortest_path_trees_deflated[source_ip][node_ip])

	def get_broadcast_neighbours(self, node_ip):
		return dc(list(self.g.neighbors(node_ip)))

	def get_nodes(self):
		names = list(self.infra.keys())
		names.remove("master")
		return dc(names)

	def get_node_ips(self):
		names = list(self.infra.keys())
		names.remove("master")

		ips = []
		for name in names:
			ips.append(self.get_ip_by_name(name))

		return dc(ips)

	def get_n_random_nodes(self, n):
		names = list(self.infra.keys())
		names.remove('master')

		links = []
		for name in names:
			links.append(self.get_ip_by_name(name))

		np.random.seed(SEED)
		return np.random.choice(links, n, replace=True)
