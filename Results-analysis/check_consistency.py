import os
import sys

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_7s/Renater20000Jobs_Cache20_40_60_seed777_7s/transient"
os.chdir(path)

for filename in os.listdir(os.getcwd()):
	if not filename.startswith('.'):
		if os.path.isdir(filename):
			print(filename)
			if filename.startswith("dht"):
				cmd =  """ grep -r "Error 404" """ + filename + "/*"
				list_of_file_not_found = os.popen(cmd).read()
				list_of_file_not_found = list_of_file_not_found.split("\n")
				del list_of_file_not_found[-1]
				nbr_of_error = len(list_of_file_not_found)
				print("404 errors: "+ str(nbr_of_error))
				for not_found_error in list_of_file_not_found:
					cluster_name = not_found_error.split("/")[1].split("-")[0]
					job_id = not_found_error.split(":")[6]
					to_grep_msg = job_id + ":DEBUG:DHT:req_time"
					to_grep_cmd = """ grep "{}" {} """.format(to_grep_msg, not_found_error.split(":")[0])
					dht_req_node = os.popen(to_grep_cmd).read()
					error_location = dht_req_node.split(",")[3].split(".")[3].split("\n")[0]
					location = not_found_error.split(",")[1].split("=")[1].split(".")[3]
					file_hash = not_found_error.split(":")[8].split("=")[1].split(',')[0]
					log_to_check = not_found_error.replace(not_found_error.split('/')[1].split("-")[0]+"-"+not_found_error.split('/')[1].split("-")[1], cluster_name+"-"+error_location).split(":")[0]
					req_msg = job_id + ":DEFAULT:{'type': 'DHT', 'subtype': 'request', 'file_hash':"+file_hash
					del_msg = "DEFAULT:{'type': 'DHT', 'subtype': 'del', 'file_hash':"+file_hash
					cmd_req = """ grep -A 500 "{}" {} """.format(req_msg, log_to_check)
					cmd_req = cmd_req.replace("\\", "")
					req_found = os.popen(cmd_req).read()
					req_found = req_found.split("\n")
					del req_found[-1]
					found_del_msg = False
					for log_entry in req_found:
						if del_msg in log_entry:
							found_del_msg = True
							print(job_id+ " - Found the DEL msg right after")
							break
					if found_del_msg == False:
						sys.exit(job_id+ " - INCONSISTENCY - No del message... - ")

			elif filename.startswith("new"):
				cmd = """ grep -r "Error 404" """ + filename + "/*"
				list_of_file_not_found = os.popen(cmd).read()
				list_of_file_not_found = list_of_file_not_found.split("\n")
				del list_of_file_not_found[-1]
				nbr_of_error = len(list_of_file_not_found)
				print("404 errors: " + str(nbr_of_error))
				for not_found_error in list_of_file_not_found:
					log_to_check = not_found_error.split(":")[0]
					job_id = not_found_error.split(":")[6]
					file_hash = not_found_error.split(":")[8].split("=")[1].split(',')[0]
					cmd_grep = """ grep -A 2500 -B 2500 "{}" {} """.format(job_id+":Error 404", log_to_check)
					req_found = os.popen(cmd_grep).read()
					req_found = req_found.split("\n")
					del req_found[-1]
					found_del_msg = False
					del_msg = "DEFAULT:{'type': 'DELETE', 'file_hash':"+file_hash
					for log_entry in req_found:
						if del_msg in log_entry:
							found_del_msg = True
							print(job_id+ " - Found the DEL msg right after")
							break
					if found_del_msg == False:
						sys.exit(job_id + " - INCONSISTENCY - No del message... - ")











