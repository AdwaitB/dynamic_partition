import sys

import networkx as nx


def generate_dict_from_yml(graphfile):
	# Run this in Topologies folder
	G = nx.read_gml(graphfile)

	ret = {"master": {}}

	names = {}
	i = 1

	for node in G.nodes():
		names[node] = i
		ret["node" + str(i)] = {}
		i = i + 1

	for edge in G.edges(data=True):
		(a, b) = (names[edge[0]], names[edge[1]])

		# Make compatible with my format
		if a > b:
			(a, b) = (b, a)
		if a == b:
			continue

		if "node" + str(b) not in ret["node" + str(a)]:
			ret["node" + str(a)]["node" + str(b)] = str(round(edge[2]['weight'])) + "ms"
	return ret


if __name__ == '__main__':
	generate_dict_from_yml(sys.argv[1])
