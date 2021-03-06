## Table Update protocol which replaces DHT

This repository consists of code that implements the table-update-protocol for finding location of object in a distributed network of nodes. The file `node_handler.py` implements this protocol as a web service. It also consists of tasks that are required to be executed on the node and a DHT request server.

This also contains the code for the master controller which controls the running of experiments that compares the performance of the DHT and the table-update protocol. The `master_controller.py` file consists of the code that performs the experiment. This talks with the web service defined in `node_handler.py` and performs the operations as deemed by the experiment.

### Generating files used for the experiment

Files of standard size are defined in `constants.py:78` which shows the multipliers used with 4KB. Hence files of sizes 4KB, 64KB ... are generated and then given a unique identifier (emulates a unique hash function). Hence after initialization, there are 8*n unique files in the system distributed evenly across the network. It is necessary to distribute them evenly as to cover all possible requests in the system.

### Job geneation

A job is defined as a node requesting for a specific file to the system. For the experiments, a job needs the node which is requesting, the identifier of the file and the time at which to execute the job. The first two are generated randomly with uniform distribution `master_controller.py:93, 96`.

The time between jobs is generated by having a base time of 0. This base time is then added with a uniform random value in milliseconds to get the time for doing the next job. So if `job_i` is scheduled at time `t_i` then `job_i+1` is scheduled at time `t_i + A + b` where a is fixed and b is generated randomly between `[0, B)`. The values of `A` and `B` can be varied in `constants.py:81, 82`.

The job schedule is generated and stored before the exeriments are run `master_controller.py:104`. Jobs where the file is already present at the node is checked while the experiment is running and do not reflect in the traces collected in the csv. They are still visible in the json file at each node which captures every message at that node.
