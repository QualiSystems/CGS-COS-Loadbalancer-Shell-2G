from cloudshell.cgs.autoload.snmp import AbstractCgsSNMPAutoload
from cloudshell.devices.standards.load_balancing.autoload_structure import GenericChassis
from cloudshell.devices.standards.load_balancing.autoload_structure import GenericPort
from cloudshell.devices.standards.load_balancing.autoload_structure import GenericResource
from cloudshell.devices.standards.load_balancing.autoload_structure import GenericServerFarm


class CgsLoadBalancerSNMPAutoload(AbstractCgsSNMPAutoload):
    LB_MIB_TABLE = "NPB-LB"
    LB_GROUP_TABLE = "lbGroupTable"

    @property
    def root_model_class(self):
        return GenericResource

    @property
    def chassis_model_class(self):
        return GenericChassis

    @property
    def port_model_class(self):
        return GenericPort

    def _build_resources(self):
        """Discover and create all needed resources.

        :return:
        """
        super(CgsLoadBalancerSNMPAutoload, self)._build_resources()
        self._build_server_farms()

    def _build_server_farms(self):
        """

        :return:
        """
        lb_groups = self.snmp_handler.get_table(self.LB_MIB_TABLE, self.LB_GROUP_TABLE)
        for lb_group in lb_groups.itervalues():
            server_farm = GenericServerFarm(shell_name=self.shell_name,
                                            name=lb_group["lbGroupName"],
                                            unique_id="{}.{}.{}".format(self.resource_name,
                                                                        "group",
                                                                        lb_group['suffix']))

            server_farm.virtual_server_port = lb_group["lbGroupOutputs"]
            server_farm.algorithm = lb_group["lbGroupAlgo"].replace("'", "")
            self.resource.add_sub_resource(lb_group['suffix'], server_farm)
