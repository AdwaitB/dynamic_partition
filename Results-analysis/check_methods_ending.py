import os

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater20000Jobs_cache10/transient"
# Get nbr of messages for AAA algo:
os.chdir(path+"/new")
dict_of_nbr_of_messages = {}
for filename in os.listdir(os.getcwd()):
	if not filename.startswith('.'):
		os.chdir(path + "/new/"+filename+"/root/deploy/traces")
		if os.path.exists(os.getcwd()+"/_node_stderr.txt"):
			cmd = """ grep  'HANDLE INSERT:START' _node_stderr.txt  """
			starts = os.popen(cmd).read()
			starts = starts.split("\n")
			del starts[-1]

			cmd = """ grep  'HANDLE INSERT:END' _node_stderr.txt  """
			ends = os.popen(cmd).read()
			ends = ends.split("\n")
			del ends[-1]

			if len(starts) != len(ends):
				print("lol")
