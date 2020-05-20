import calendar
import os
import re
import shutil
import time
from threading import Thread

from execo_g5k import *


# Testing if I can commit to this repo.

def delete_file_if_exists(file_name):
	try:
		os.remove(file_name)
	except:
		pass


def delete_folder_if_exists(folder_name):
	try:
		shutil.rmtree(folder_name)
	except:
		pass


def delete_folder_regex(pattern):
	search = os.path.dirname(os.path.abspath(__file__))
	inner = os.listdir(search)
	for dire in inner:
		if re.search(pattern, dire):
			delete_folder_if_exists(search + "/" + dire)


def cleanup():
	# delete_file_if_exists("Vagrantfile")
	delete_file_if_exists("current")
	delete_folder_if_exists("_tmp_enos_")
	delete_folder_if_exists("current")
	# delete_folder_if_exists(".vagrant")
	delete_folder_regex("enos*")


class OarKeepAlive(Thread):
	def __init__(self, jobid, site):
		Thread.__init__(self)

		self.ongoing = True

		self.jobid = jobid
		self.site = site

	def run(self):
		print("Starting thread for keeping the OAR Job {} alive".format(self.jobid))

		while self.ongoing:
			# Wait for 5 mins
			time.sleep(5 * 60)

			# Check if extention is needed
			job_info = get_oar_job_info(self.jobid, self.site)
			seconds_before_job_end = job_info.get("start_date") + job_info.get("walltime") - calendar.timegm(
				time.gmtime())

			print("Job {} finishes in {} seconds".format(self.jobid, seconds_before_job_end))

			# If yes, do the extention
			if seconds_before_job_end < 60 * 10:
				print("Job {} finishes in {} seconds, extending.".format(self.jobid, seconds_before_job_end))
				os.system("ssh {}.grid5000.fr oarwalltime {} +0:30".format(self.site, self.jobid))
