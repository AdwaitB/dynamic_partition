import copy
import logging
import threading
from copy import deepcopy
from datetime import datetime as dt
from infra_parser import *

logging.basicConfig(level=logging.DEBUG)


class LockedEntry:
	def __init__(self, entry):
		self.entries = set()
		self.entries.add(entry)

		self.lock = threading.Lock()

	def get_entries(self):
		return copy.deepcopy(self.entries)

	def update_entry(self, entry):
		self.lock.acquire()
		self.entries.add(entry)
		self.lock.release()
		return 0

	def delete_entry(self, entry):
		self.lock.acquire()
		self.entries.remove(entry)
		self.lock.release()
		return 0

	def is_empty(self):
		return len(self.entries) == 0


class Table:
	def __init__(self):
		self.entries = {}  # <file_id, LockedEntry>
		self.parent_lock = threading.Lock()  # Master lock while deleting and adding
		self.clock = 0

		self.infra = Infra()

		self.my_ip = LOCALHOST
		self.master_ip = self.infra.get_ip_by_name("master")

		self.src_ips = {}
		self.dht_ips = {}

		self.node_mapping = {}

		self.n = len(self.infra.get_nodes())

	def update_my_ip(self, ip):
		self.my_ip = ip

	def get_entries_for_file(self, file_id):
		if file_id in self.entries:
			return self.entries[file_id].get_entries()
		else:
			return []

	def remove_entry_for_file(self, file_id, entry):
		if file_id not in self.entries:
			return 1
		else:
			self.entries[file_id].delete_entry(entry)

			self.parent_lock.acquire()
			if self.entries[file_id].is_empty():
				del self.entries[file_id]
			self.parent_lock.release()

	def update_entries_for_file(self, file_id, entry):
		"""
		Updates the entries for a file.
		If the file doesn't exist (in case a replica is added to some other node which is nearer),
			then the file is added to entries
		Else, the entries are updated
		:param file_id: the file ip
		:param entry: The entry to be updated
		:return:
		"""
		if file_id in self.entries:
			self.entries[file_id].update_entry(entry)
		else:
			self.entries[file_id] = LockedEntry(entry)

	def get_best_entry_for_file(self, file_id):
		"""
		Gets the nearest replica or source of the file id provided
		:param file_id: <file_hash, source_ip>
		:return: An entry <ip, clock> of the closest replica
		"""
		# Initialize entry to source
		src_ip = file_id[1]
		ret = (src_ip, 0)
		min_dist = self.infra.shortest_path_dist[src_ip][self.my_ip]

		if file_id in self.entries:
			entries = self.get_entries_for_file(file_id)
			for entry in entries:
				replica_ip = entry[0]
				if self.infra.shortest_path_dist[replica_ip][self.my_ip] < min_dist:
					ret = entry
					min_dist = self.infra.shortest_path_dist[replica_ip][self.my_ip]

		return ret

	def handle_insert(self, file_id, job_id):
		"""
		Handles the insert of file in current node.
		Creates a new entry of file if file doesnt already exists and returns SPT neighbours
			rooted at this node for replica propogation
		Else if file exists, it does nothing and returns an empty list
		Also returns a clock
		:param file_id: <file_hash, file_source> pair
		:return: [list of neighbours], clock
		"""

		logging.debug("{}:JOB ID {}:ROUTING INSERT:START:".format(dt.now(), job_id))

		self.parent_lock.acquire()
		self.clock = self.clock + 1
		if file_id in self.entries:
			self.entries[file_id].update_entry((self.my_ip, self.clock))
		else:
			self.entries[file_id] = LockedEntry((self.my_ip, self.clock))
		self.parent_lock.release()

		logging.debug("{}:JOB ID {}:ROUTING INSERT:END:".format(dt.now(), job_id))

		return self.infra.get_spt_neighbours(self.my_ip, self.my_ip), self.clock

	def handle_add(self, file_id, remote_entry, job_id):
		"""
		Handles the add message received from other node
		Returns the list of SPT neighbours to send an update to.
		This list is empty if the remote entry is not better than what is already present
		:param file_id: <file_hash, file_source> pair
		:param remote_entry: <ip, clock> for the added file
		:return: [list of neighbours]
		"""
		logging.debug("{}:JOB ID {}:ROUTING ADD:START:".format(dt.now(), job_id))

		# Find the best location of this object. Can be source and not necessary that this object has an entry.
		best = self.get_best_entry_for_file(file_id)

		logging.debug("{}:JOB ID {}:ROUTING ADD:current_best = {}".format(dt.now(), job_id, best))

		# If the best distance is not better than what was passed to function, update the table
		if self.infra.shortest_path_dist[best[0]][self.my_ip] > self.infra.shortest_path_dist[remote_entry[0]][
			self.my_ip]:
			# This entry is better, add this to the local set
			logging.debug(
				"{}:JOB ID {}:ROUTING ADD:new_entry_added = (file_id = {}, remote_entry = {})".format(dt.now(), job_id, file_id, remote_entry))
			self.update_entries_for_file(file_id, remote_entry)

			# Return a list of neighbours that need to be notified
			return self.infra.get_spt_neighbours(remote_entry[0], self.my_ip)

		# This entry is not better, do not update any neighbouring nodes
		return []

	def handle_remove(self, file_id, job_id):
		"""
		Handle a remove statements
		:param file_id: <file_hash, file_source> pair
		:return: old_best, new_best, broadcast_neighbours
		"""
		logging.debug("{}:JOB ID {}:ROUTING REMOVE:START:".format(dt.now(), job_id))

		# Get the current entry which should be self. Call this old_best
		old_best = self.get_best_entry_for_file(file_id)

		# Remove this entry
		self.remove_entry_for_file(file_id, old_best)

		# Find the new best entry
		new_best = self.get_best_entry_for_file(file_id)

		logging.debug("{}:JOB ID {}:ROUTING REMOVE:END:old_best = {}, new_best = {}, neighbours = {}".format(
			dt.now(), job_id, old_best, new_best, self.infra.get_broadcast_neighbours(self.my_ip))
		)

		# Broadcast this entry
		return old_best, new_best, self.infra.get_broadcast_neighbours(self.my_ip)

	def handle_del(self, file_id, remove_src_entry, sender_ip, sender_entry, job_id):
		logging.debug("{}:JOB ID {}:ROUTING DEL:START:".format(dt.now(), job_id))

		# Find set for condition 1
		old_clocks = self.get_entries_for_file(file_id)

		# Remove entries from this list which have a newer clock (as we do not delete those)
		# This is the contrapositive of the condition in the doc. We remove here the entries that are not be deleted
		#   from the alive set
		for old_clock in self.get_entries_for_file(file_id):
			if old_clock[1] > remove_src_entry[1] or old_clock[0] != remove_src_entry[0]:
				old_clocks.remove(old_clock)

		# olc_clocks satisfies 1

		ret = {RequestType.DELETE.name: {}, RequestType.ADD.name: {}}

		logging.debug("{}:JOB ID {}:ROUTING DEL:old_entries = {}".format(dt.now(), job_id, old_clocks))

		# Check 1
		if len(old_clocks) > 0:
			logging.debug("{}:JOB ID {}:ROUTING DEL:BEFORE:file_id = {}: my_entries = {}".format(dt.now(), job_id, file_id, str(self.entries[file_id].entries)))

			# Remove the stale entries
			for old_clock in old_clocks:
				self.entries[file_id].delete_entry(old_clock)

			logging.debug("{}:JOB ID {}:ROUTING DEL:AFTER:file_id = {}: my_entries = {}".format(dt.now(), job_id, file_id, str(self.entries[file_id].entries)))
			# The new best
			new_best = self.get_best_entry_for_file(file_id)

			ret[RequestType.DELETE.name]["neighbours"] = self.infra.get_broadcast_neighbours(self.my_ip)
			if new_best == sender_entry:
				ret[RequestType.DELETE.name]["neighbours"].remove(sender_ip)
			ret[RequestType.DELETE.name]["new_best"] = new_best

			# Send to neighbours
			logging.debug("{}:JOB ID {}:ROUTING DEL:DEL BROADCAST:neighbours = {}".format(dt.now(), job_id, ret[RequestType.DELETE.name]["neighbours"]))

		else:
			new_best = self.get_best_entry_for_file(file_id)

		if sender_ip in self.infra.get_spt_neighbours(self.my_ip, self.my_ip) \
				and new_best[0] != file_id[1] \
				and new_best != sender_entry:
			logging.debug("{}:JOB ID {}:ROUTING DEL:ADD RETURN:".format(dt.now(), job_id))

			ret[RequestType.ADD.name]["ip"] = sender_ip
			ret[RequestType.ADD.name]["new_best"] = new_best

		logging.debug("{}:JOB ID {}:ROUTING DEL:END:new_best = {}".format(dt.now(), job_id, new_best))
		return ret

	def get_snapshot(self):
		ret = {}

		for file_id in self.entries:
			ret[file_id[0]] = {}
			ret[file_id[0]]['entries'] = list(self.entries[file_id].get_entries())
			ret[file_id[0]]['src'] = file_id[1]

		ret['dht_ips'] = self.dht_ips

		return ret

	def generate_dht_src(self):
		for fh in self.src_ips:
			if int(fh) % self.n == self.node_mapping[self.my_ip]:
				self.dht_ips[fh] = [deepcopy(self.src_ips[fh]['source'])]

		logging.debug("{}:dht_ips = {}".format(dt.now(), self.dht_ips))

	def get_ip_by_value(self, value):
		for ip in self.node_mapping:
			if self.node_mapping[ip] == value:
				return ip
		return LOCALHOST
