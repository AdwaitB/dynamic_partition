import os
import json

path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Renater/Jobs_50ms/transient"
os.chdir(path)

dict_nb_errors = {}
for filename in os.listdir(os.getcwd()):
    if not filename.startswith('.'):
        if os.path.isdir(filename):
            print(filename)
            cmd = """ grep -r "Error 404" """ + filename + "/*" + "| wc -l"
            nb_errors = int(os.popen(cmd).read())
            dict_nb_errors[filename] = nb_errors

print(json.dumps(dict_nb_errors, indent = 4))

