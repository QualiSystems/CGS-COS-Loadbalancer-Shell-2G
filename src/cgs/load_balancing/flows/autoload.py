from cloudshell.cgs.flows.autoload import CgsSnmpAutoloadFlow

from cgs.load_balancing.autoload.snmp import CgsLoadBalancerSNMPAutoload


class CgsLoadBalancerSnmpAutoloadFlow(CgsSnmpAutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        with self._snmp_handler.get_snmp_service() as snmp_service:
            f5_snmp_autoload = CgsLoadBalancerSNMPAutoload(snmp_handler=snmp_service,
                                                           shell_name=shell_name,
                                                           shell_type=shell_type,
                                                           resource_name=resource_name,
                                                           logger=self._logger)
            return f5_snmp_autoload.discover(supported_os)
