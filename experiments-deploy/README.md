## Deploy Infra and Run Experiments

This repo contains the code to run the experiments. It only hanldes the setup of the experiment. This includes the following:
1. The infra deployment using defined topology.
2. Creating network emulation given in the topology.
3. Copy code files, demo files and directores for storing result.
4. Fetch the result, and plot the finalized graphs. The enos session needs to be active to do this, hence even if the experiment is over, the `destroy` is only called after post-processing is over.
5. Keeping the OAR Job active. The default reservation is for 2 hours. If needed, it is increased by 30 mins increments.

### Steps to deploy

1. Use this [link](https://gitlab.inria.fr/abauskar1/ipfs-notes/blob/master/setup_experiments.sh) to set up the experiments.

2. Run `sudo apt-get install python3-tk` for using matplotlib.

3. Run experiments.py from the virtualenv.

- Image required to run can be created using [this](https://gitlab.inria.fr/abauskar1/ipfs-notes/blob/master/build_image.sh).
- The parameters can be set in `infra.py` for the infra. It is assumed that there is a `master` node and all the other nodes are of the form `nodex` where x is numeric.
- For changing the infra, point to the appropriate variable in `experiments.py`.
- The script `parse_gml.py` can be used to convert `.gml` files. Pass the `.gml` file as a command line parameter, then the output is pretty printed which can be copy pasted into `infra.py`. Unfortunately, there is no better way for now.
- The job generation happens online in the master. So the job generation parameters are in `constants.py` in the [protocol code](https://gitlab.inria.fr/abauskar1/ipfs-table-update-backend).
