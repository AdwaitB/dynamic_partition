import datetime
import pandas as pd


class File:
	def __init__(self, file_name, file_hash):
		'''
		Create a File with the following
		:param file_name: Name of the file
		:param file_hash: Hash of the file
		:param node_hash: Hash of the node
		'''
		self.file_name = file_name
		self.file_hash = file_hash
		self.node_hashes = []

		self.timestamp = datetime.datetime.now()

	def add_node(self, node_hash):
		'''
		Adds a node to the file. Replicas are stored this way
		:param node_hash: Hash of the node
		:return: False if it was already present
		'''
		if node_hash not in self.node_hashes:
			self.node_hashes.append(node_hash)
			return True
		else:
			return False

	def delete_node(self, node_hash):
		'''
		Deletes a node from the file. Replicas are removed this way
		:param node_hash:
		:return: False if it was not present
		'''
		if node_hash in self.node_hashes:
			while node_hash in self.node_hashes:
				self.node_hashes.remove(node_hash)
			return True
		else:
			return False

	def get_nodes(self):
		'''
		Get the nodes for this file
		:return: Returns a list of hashes of the nodes for this file
		'''
		return self.node_hashes

	def __str__(self):
		'''
		String print
		:return: string of the whole data of the file.
		'''
		ret = ""
		ret = ret + self.file_hash + "|" + self.file_name + "|" + str(len(self.node_hashes)) + "\n"
		for node_hash in self.node_hashes:
			ret = ret + node_hash + "\n"
		return ret


class Node:
	def __init__(self, node_name, node_hash):
		'''
		Creates a ipfs node with name and its ipfs hash
		:param node_name: node name
		:param node_hash: ipfs hash of the node
		'''
		self.node_name = node_name
		self.node_hash = node_hash
		self.timestamp = datetime.datetime.now()

		self.file_hashes = []

	def add_file(self, file_hash):
		'''
		Adds a file to this node
		:param file_hash: hash of the file
		:return: False if the file is already present
		'''
		if file_hash not in self.file_hashes:
			self.file_hashes.append(file_hash)
			return True
		else:
			return False

	def delete_file(self, file_hash):
		'''
		Deletes a file from this node
		:param file_hash: Hash of the file
		:return: False if it was not present
		'''
		if file_hash in self.file_hashes:
			while file_hash in self.file_hashes:
				self.file_hashes.remove(file_hash)
			return True
		else:
			return False

	def get_files(self):
		'''
		Get the hash of all the files stored on this node
		:return: List of hash of files on this node
		'''
		return self.file_hashes

	def __str__(self):
		'''
		Enumerate all the data of this node
		:return: String of the data in this node
		'''
		ret = ""
		ret = ret + self.node_hash + "|" + self.node_name + "|" + str(len(self.file_hashes)) + "\n"
		for file_hash in self.file_hashes:
			ret = ret + file_hash + "\n"
		return ret


class FilesDB:
	def __init__(self):
		self.file_by_name = {}
		self.files_by_hash = {}

		# Hash of the file : The actual file
		self.files = {}

	def add_file(self, file_name, file_hash):
		'''
		Add a new file to the system
		:param file_name: Name of the file
		:param file_hash: hash of the file
		:param node_hash: hash of the node
		:return: False if file is already present
		'''
		if file_hash in self.files:
			return False

		self.file_by_name[file_name] = file_hash
		self.files_by_hash[file_hash] = file_name

		self.files[file_hash] = File(file_name, file_hash)
		return True

	def add_replica(self, file_hash, node_hash):
		'''
		Add a replica to the system
		:param file_hash: Hash of the file
		:param node_hash: Hash of the node
		:return: False if the file does not exist
		'''
		if file_hash not in self.files:
			return False

		self.files[file_hash].add_node(node_hash)
		return True

	def delete_file_from_node(self, file_hash, node_hash):
		'''
		Deletes the file from the node.
		:param file_hash: ipfs_hash of the file
		:param node_hash:
		:return: False if file was not present
		'''
		if file_hash in self.files:
			self.files[file_hash].delete_node(node_hash)
			return True
		else:
			return False

	def get_file_by_hash(self, file_hash):
		'''
		Gets the file name by its hash. Return -1 if it does not exist
		:param file_hash: Hash of the file
		:return: string of the name of the file, -1 if it does not exist
		'''
		if file_hash in self.files_by_hash:
			return self.files_by_hash[file_hash]
		else:
			return -1

	def get_file_by_name(self, file_name):
		'''
		Gets the file hash by its name. Return -1 if it does not exist
		:param file_name: Name of the file
		:return: String of the hash, -1 if it does not exist
		'''
		if file_name in self.file_by_name:
			return self.file_by_name[file_name]
		else:
			return -1


class NodeDB:
	def __init__(self, infra):
		self.node_by_name = {}
		self.node_by_hash = {}

		self.nodes = {}

	def add_node(self, node_name, node_hash):
		'''
		Adds node to the node DB.
		Initialized during the initialization of the IPFS repo
		:param node_name: Node as in the infra
		:param node_hash: Hash of the ipfs node
		:return: False if the node is present in the infra
		'''

		if node_hash in self.nodes:
			return False

		self.node_by_hash[node_hash] = node_name
		self.node_by_name[node_name] = node_hash

		self.nodes[node_hash] = Node(node_name, node_hash)
		return True

	def add_replica(self, file_hash, node_hash):
		'''
		Adds a replica of file file in a node
		:param file_hash: hash of the file
		:param node_hash: hash of the node
		:return: False if the node does not exist
		'''
		if node_hash not in self.nodes:
			return False

		self.nodes[node_hash].add_file(file_hash)
		return True

	def delete_file_from_node(self, file_hash, node_hash):
		'''
		Deletes a replica of file from the node
		:param file_hash: hash of the file
		:param node_hash: hash of the node
		:return: False if the node did not exist
		'''
		if node_hash not in self.nodes:
			return False
		else:
			self.nodes[node_hash].delete_file(file_hash)
			return True

	def get_node_by_hash(self, node_hash):
		'''
		Get the node name by hash
		:param node_hash: ipfs hash of the node
		:return: name of the node if it exists else -1
		'''
		if node_hash in self.node_by_hash:
			return self.node_by_hash[node_hash]
		else:
			return -1

	def get_node_by_name(self, node_name):
		'''
		Get the node hash by its name
		:param node_name: Name of the node
		:return: hash of the node if it exists else -1
		'''
		if node_name in self.node_by_name:
			return self.node_by_name[node_name]
		else:
			return -1


class DB:
	def __init__(self, infra):
		self.ndb = NodeDB()
		self.fdb = FilesDB()
		self.infra = infra
		self.trace = pd.DataFrame(columns=["type", "node_name", "file_name", "timestamp"])

	def new_node(self, node_name, node_hash):
		'''
		Adds a node to the DB
		:param node_name: name of the node
		:param node_hash: hash of the node
		:return: true if node is present in infra else false
		'''
		entry = {"type": "add_node",
				 "node_name": node_name,
				 "file_name": "",
				 "timestamp": datetime.datetime.now()}
		self.trace = self.trace.append(entry)
		self.ndb.add_node(node_name, node_hash)

	def new_file(self, file_name, file_hash):
		'''
		Adds file to the node
		:param node_name: Name of the node
		:param file_name: Name of the file
		:param file_hash: hash of the file
		:return: True if node exists and file is added
		'''

		entry = {"type": "add_file",
				 "node_name": "",
				 "file_name": file_name,
				 "timestamp": datetime.datetime.now()}
		self.trace = self.trace.append(entry)
		self.fdb.add_file(file_name, file_hash)

	def add_replica(self, file_name, node_name):
		'''
		Creates a replica of the file in the node
		:param file_name: Name of the file
		:param node_name: Name of the node
		:return: ~
		'''
		file_hash = self.fdb.get_file_by_name(file_name)
		node_hash = self.ndb.get_node_by_name(node_name)

		self.fdb.add_replica(file_hash, node_hash)
		self.ndb.add_replica(file_hash, node_hash)

		entry = {"type": "add_replica",
				 "node_name": node_name,
				 "file_name": file_name,
				 "timestamp": datetime.datetime.now()}
		self.trace = self.trace.append(entry)

	def delete_replica(self, file_name, node_name):
		'''
		Deletes a replica of the file in the node
		:param file_name: Name of the file
		:param node_name: Name of the node
		:return: ~
		'''
		file_hash = self.fdb.get_file_by_name(file_name)
		node_hash = self.ndb.get_node_by_name(node_name)

		self.fdb.add_replica(file_hash, node_hash)
		self.ndb.add_replica(file_hash, node_hash)

		entry = {"type": "add_replica",
				 "node_name": node_name,
				 "file_name": file_name,
				 "timestamp": datetime.datetime.now()}
		self.trace = self.trace.append(entry)

	def trace_write(self, path):
		self.trace.to_csv(path + "/transient.csv")
