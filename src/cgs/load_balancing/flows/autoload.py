from cloudshell.cgs.flows.autoload import AbstractCgsSnmpAutoloadFlow

from cgs.load_balancing.autoload.snmp import CgsLoadBalancerSNMPAutoload


class CgsLoadBalancerSnmpAutoloadFlow(AbstractCgsSnmpAutoloadFlow):
    @property
    def snmp_autoload_class(self):
        return CgsLoadBalancerSNMPAutoload
