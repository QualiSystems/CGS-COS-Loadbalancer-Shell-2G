from cloudshell.cgs.runners.autoload import CgsAutoloadRunner

from cgs.load_balancing.flows.autoload import CgsLoadBalancerSnmpAutoloadFlow


class CgsLoadBalancerAutoloadRunner(CgsAutoloadRunner):
    @property
    def autoload_flow(self):
        return CgsLoadBalancerSnmpAutoloadFlow(self.snmp_handler, self._logger)
