from pprint import pprint as pp

import networkx as nx


class Infra:
	def __init__(self, infra):
		self.infra = infra

		self.g = self.build_graph()
		self.shortest_path_dist = dict(nx.all_pairs_dijkstra_path_length(self.g))

		print("shortest_path_dist")
		pp(self.shortest_path_dist)

	def build_graph(self):
		ret = nx.Graph()
		for node in self.infra:
			ret.add_node(node)

		for node in self.infra:
			for other_node in self.infra[node]:
				edge_weight = int(self.infra[node][other_node][:-2])
				ret.add_edge(node, other_node, weight=edge_weight)
		return ret

	@staticmethod
	def get_alias_by_name(roles, name):
		roles_dict = []
		for role in roles:
			for machine in roles[role]:
				machine = machine.to_dict()
				machine.update(role=role)
				roles_dict.append(machine)

		for role in roles_dict:
			if role['role'] == name:
				return role['alias']
