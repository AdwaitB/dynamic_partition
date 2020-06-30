import os
import string
import subprocess
from enoslib.infra.enos_g5k.configuration import Configuration, NetworkConfiguration
from enoslib.infra.enos_g5k.provider import G5k
from infra import g5k_cluster, g5k_loc, g5k_image


class G5KProvider:
    def __init__(self, infra, image=g5k_image):
        self.conf = self.create_configuration(infra, image)
        self.provider = 0
        self.job_id = 0

        f = open("{}/.python-grid5000.yaml".format(os.path.expanduser("~")), "r")
        for line in f.readlines():
            if "username" in line:
                self.user = line.split(":")[1]
                self.user = self.user.translate({ord(c): None for c in string.whitespace})
        print("User: " + self.user)

    @staticmethod
    def create_configuration(infra, image):
        # Building the configuration for connection
        conf = Configuration.from_settings(job_name="experiments",
                                           env_name=image)

        # Claim the resources
        # Create the network
        network = NetworkConfiguration(id="n1",
                                       type="kavlan",
                                       roles=["my_network"],
                                       site=g5k_loc)
        conf.add_network_conf(network)

        for node in list(infra.keys()):
            conf.add_machine(roles=[node],
                             cluster=g5k_cluster,
                             nodes=1,
                             primary_network=network)

        conf.walltime = "16:00:00"

        conf.finalize()
        return conf

    def deploy_infra(self):
        # Starting the machines
        self.provider = G5k(self.conf)
        roles, networks = self.provider.init()

        self.get_job_id()
        print("job_id: " + str(self.job_id))

        return roles, networks

    def get_job_id(self):
        output = subprocess.check_output("ssh " + g5k_loc + ".grid5000.fr oarstat", shell=True)
        output = output.decode()

        print("job_id (output):" + str(output))

        for line in str(output).split('\n'):
            print("job_id (output):" + str(line))
            if self.user in str(line):
                print("> " + line)
                val = line.split(sep=" ")
                self.job_id = int(val[0])
                return

    def destroy(self):
        self.provider.destroy()
