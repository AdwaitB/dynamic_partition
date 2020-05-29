import json
import os
import time

from enoslib.api import run_ansible


class PlayBook:
	def __init__(self, roles, networks, infra):
		self.roles = roles
		self.networks = networks
		self.trace = {}
		self.infra = infra

		self.roles_dict = []
		for role in roles:
			for machine in roles[role]:
				machine = machine.to_dict()
				machine.update(role=role)
				self.roles_dict.append(machine)

		print(roles)

		infra_json = {"infra": infra, "roles": self.roles_dict, "network": networks}
		self.infra_json = json.dumps(infra_json)

		if not os.path.exists('./transient'):
			os.makedirs('./transient')

		with open('./transient/infra.json', 'w') as json_file:
			json.dump({"infra": infra, "roles": self.roles_dict, "network": networks}, json_file)

	def initialize_files(self):
		# Clean the instance first
		run_ansible(['playbooks/clean_backend.yaml'], roles=self.roles)

		# Now reinitalize the files
		run_ansible(['playbooks/copy_backend_files.yaml'], roles=self.roles)

	def start_services(self, iteration):
		run_ansible(['playbooks/node_services.yaml'], roles=self.roles)
		run_ansible(['playbooks/master_services.yaml'], roles=self.roles, extra_vars={"iteration": iteration})

		# Give time for Flask to start. Might take time on Vagrant
		time.sleep(10)
		return

	def fetch(self, iteration):
		run_ansible(['playbooks/fetch_result.yaml'], roles=self.roles, extra_vars={"iteration": iteration})

	def write_trace(self):
		with open("output/result.json", "w") as f:
			json.dump(self.trace, f, indent=2)
