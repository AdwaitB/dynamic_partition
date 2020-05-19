'Limit size, evicting the least recently looked-up key when full'
import collections


# This implementation only limits the *number* of elements in the cache
# It does not take into account the size of each elements, as we only deal with small file sizes.
# i.e. if max filesize < 20MB and capacity = 100 then 2GB cache size is enough
class LRUCache:
	# @param capacity, an integer
	def __init__(self, capacity):
		self.capacity = capacity
		self.cache = collections.OrderedDict()

	# @return an integer
	def get(self, key):
		if not key in self.cache:
			return -1
		value = self.cache.pop(key)
		self.cache[key] = value
		return value

	# @param key, an integer
	# @param value, an integer
	# @return nothing
	def set(self, key, value):
		file_hash = 0
		if key in self.cache:
			self.cache.pop(key)
		elif len(self.cache) == self.capacity:
			file_hash = self.cache.popitem(last=False)[0]
		self.cache[key] = value
		return file_hash

# This version takes into account the size of objects. Problem: can generate burst of Deletes
# e.g. if capacity = 10MB , and there is 1000 files of 10KB in cache, to put a 9MB file in cash, need to remove the 1000 files.
# Actually not necessarily worst with our protocol as we can group all the 1000 DEL in the same msg to broadcast.
#     class LRUCache:
#         # @param capacity, an integer
#         def __init__(self, capacity):
#             self.capacity = capacity
#             self.cache = collections.OrderedDict()
#             self.current_load = 0
#
#         # @return an integer
#         def get(self, key):
#             if not key in self.cache:
#                 return -1
#             value = self.cache.pop(key)
#             self.cache[key] = value
#             return value
#
#         # @param key, an integer
#         # @param value, an integer
#         # @return nothing
#         def set(self, key, value):
#             file_hash = 0
#             if value > self.capacity:  # Object can not be stored in the cache.
#                 return -1
#             else:
#                 if key in self.cache:
#                     self.cache.pop(key)
#                 elif self.current_load + value > self.capacity:
#                     file_hash = self.cache.popitem(last=False)[0]
#                 self.cache[key] = value
#                 self.current_load += value
#             return file_hash
