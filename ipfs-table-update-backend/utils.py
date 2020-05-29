import logging
from concurrent.futures import ThreadPoolExecutor
import requests

from .constants import *

logging.basicConfig(level=logging.DEBUG)


def append_entry(d, name, value):
	d[name] = value
	return d


def generate_url(ip=LOCALHOST, port=NODE_CUSTOM_PORT):
	return "http://" + ip + ":" + port


def load_url(url, json_file):
	return requests.post(url, json=json_file, timeout=HTTP_TIMEOUT)


def post_multiple(ips, request_jsons, do_async_local):
	if len(ips) != len(request_jsons):
		return None

	ret = {}

	if do_async_local and len(ips) > 0:
		size = min(len(ips), 20)

		executor = ThreadPoolExecutor(max_workers=size)
		for ip, output in zip(ips, executor.map(load_url, [generate_url(x) for x in ips], request_jsons)):
			if ip in ret:
				ret[ip].append(output.text)
			else:
				ret[ip] = [output.text]
	else:
		for i in range(len(ips)):
			output = load_url(generate_url(ips[i]), request_jsons[i])
			if ips[i] in ret:
				ret[ips[i]].append(output.text)
			else:
				ret[ips[i]] = [output.text]

	return ret
