from enoslib.infra.enos_vagrant.configuration import Configuration
from enoslib.infra.enos_vagrant.provider import Enos_vagrant
from infra import vagrant_image


class VagrantProvider:
    def __init__(self, infra, image=vagrant_image):
        self.conf = self.create_configuration(infra, image)
        self.provider = 0

    @staticmethod
    def create_configuration(infra, image):
        # Building the configuration for connection
        conf = Configuration.from_settings(backend="virtualbox",
                                           box=image)

        # Claim the resources
        for node in list(infra.keys()):
            conf.add_machine(roles=[node],
                             flavour="small",
                             number=1)

        conf.add_network(roles=["my_network"],
                         cidr="192.168.42.0/24")

        conf.finalize()
        return conf

    def deploy_infra(self):
        # Starting the machines
        self.provider = Enos_vagrant(self.conf)
        roles, networks = self.provider.init()
        return roles, networks

    def destroy(self):
        self.provider.destroy()
