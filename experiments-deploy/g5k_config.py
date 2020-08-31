import os
import string
import subprocess
from enoslib.infra.enos_g5k.configuration import Configuration, NetworkConfiguration
from enoslib.infra.enos_g5k.provider import G5k
from infra import g5k_cluster, g5k_loc, g5k_image, NBR_OF_PHY_MACHINES
import enoslib.infra.enos_vmong5k.configuration as vmconf
from enoslib.infra.enos_vmong5k.provider import start_virtualmachines
import enoslib.infra.enos_g5k.configuration as g5kconf
from enoslib.api import discover_networks

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
        CLUSTER = g5k_cluster
        SITE = g5k_loc
        print(infra)

        prod_network = g5kconf.NetworkConfiguration(
            id="n1",
            type="prod",
            roles=["my_network"],
            site=SITE)
        conf = (
            g5kconf.Configuration
                .from_settings(
                job_type="allow_classic_ssh",
                job_name="placement"
            )
                .add_network_conf(prod_network)
                .add_network(
                id="not_linked_to_any_machine",
                type="slash_22",
                roles=["my_subnet"],
                site=SITE
            ))

        for i in range(0, NBR_OF_PHY_MACHINES):
            conf.add_machine(
                roles=["machine{}".format(i)],
                cluster=CLUSTER,
                nodes=1,
                primary_network=prod_network
            )

        conf.walltime = "13:30:00"
        conf.finalize()
        return conf

    def deploy_infra(self, infra):
        # Starting the machines
        self.provider = G5k(self.conf)
        roles, networks = self.provider.init()
        roles = discover_networks(roles, networks)

        # Retrieving subnet
        subnet = [n for n in networks if "my_subnet" in n["roles"]]

        # We describe the VMs types and placement in the following
        virt_conf = (
            vmconf.Configuration
                .from_settings(image=g5k_image))
        # Starts some vms on a single role
        # Here that means start the VMs on a single machine
        j = 0
        for node in list(infra.keys()):
            print(node)
            virt_conf.add_machine(
                roles=[node],
                number=1,
                undercloud=roles["machine{}".format(j % NBR_OF_PHY_MACHINES)],
                flavour="large"
            )
            j = j + 1
            if (j % NBR_OF_PHY_MACHINES) == 0: j = j + 1
        virt_conf.finalize()

        # Start them
        vmroles, networks = start_virtualmachines(virt_conf, subnet)
        roles = discover_networks(vmroles, networks)

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
