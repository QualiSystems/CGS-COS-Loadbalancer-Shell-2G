from cloudshell.cgs.runners.autoload import AbstractCgsAutoloadRunner

from cgs.load_balancing.flows.autoload import CgsLoadBalancerSnmpAutoloadFlow


class CgsLoadBalancerAutoloadRunner(AbstractCgsAutoloadRunner):
    @property
    def autoload_flow(self):
        return CgsLoadBalancerSnmpAutoloadFlow(self.snmp_handler, self._logger)
