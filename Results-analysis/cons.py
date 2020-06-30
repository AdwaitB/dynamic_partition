import os
import csv
import datetime
from datetime import datetime

MAX_NUMBER_JOBS = 20000
path = "/Users/avankemp/Workspace/Triple-A/Experiments/G5K/Interval_5s/Renater20000Jobs_Cache20_40_60_seed777_5s/transient"

def get_jobID_set():
    jobID_set = set()
    os.chdir(path)
    cmd = """ find  ./* -name "traces-*.csv" """
    data_path = os.popen(cmd).read()
    data_path = data_path.split("\n")
    data_path = [x for x in data_path if "small" not in x and x != """"""""]
    counter = 0
    for csv_file in data_path:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the first line with names of columns
            for row in reader:
                if counter < MAX_NUMBER_JOBS:
                    jobID_set.add(row[4].replace(".0", ""))
                    counter += 1
            return jobID_set

def get_stop_time(xp, cache_size):
    counter = 0
    csv_file = path + '/traces-{}.csv'.format(cache_size)
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first line with names of columns
        for row in reader:
            if counter < MAX_NUMBER_JOBS:
                counter += 1
            else:
                break

        if xp == 'dht':
            #return datetime.strptime(row[6], "%Y-%m-%w %H:%M:%S.%f")
            return datetime.fromisoformat(row[6])
        elif xp == 'new':
            #return datetime.strptime(row[15], "%Y-%m-%w %H:%M:%S.%f")
            return datetime.fromisoformat(row[15])







if __name__ == '__main__':
    #setID = get_jobID_set()
    #print(sorted([int(x) for x in setID]))
    print(get_stop_time('new', 20))
    
    
    
    
    
