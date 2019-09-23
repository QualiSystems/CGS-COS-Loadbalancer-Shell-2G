from cloudshell.cgs.snmp.handler import CgsSnmpHandler
from cloudshell.cgs.cli.handler import CgsCliHandler
from cloudshell.cgs.runners.autoload import CgsAutoloadRunner
from cloudshell.cgs.runners.configuration import CgsConfigurationRunner
from cloudshell.cgs.runners.firmware import CgsFirmwareRunner
from cloudshell.cgs.runners.state import CgsStateRunner
from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.devices.driver_helper import get_api
from cloudshell.devices.driver_helper import get_cli
from cloudshell.devices.driver_helper import get_logger_with_thread_id
from cloudshell.devices.driver_helper import parse_custom_commands
from cloudshell.devices.standards.load_balancing.configuration_attributes_structure import \
    create_load_balancing_resource_from_context
from cloudshell.devices.runners.run_command_runner import RunCommandRunner
from cloudshell.shell.core.driver_utils import GlobalLock
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class CgsCosLoadbalancerShell2GDriver(ResourceDriverInterface, GlobalLock):
    SUPPORTED_OS = [r"COS"]
    SHELL_NAME = "CGS COS Loadbalancer Shell 2G"

    def __init__(self):
        """ctor must be without arguments, it is created with reflection at run time"""
        super(CgsCosLoadbalancerShell2GDriver, self).__init__()
        self._cli = None

    def initialize(self, context):
        """Initialize the driver session, this function is called everytime a new instance of the driver is created

        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                      supported_os=self.SUPPORTED_OS,
                                                                      context=context)

        session_pool_size = int(resource_config.sessions_concurrency_limit)
        self._cli = get_cli(session_pool_size)

        return 'Finished initializing'

    @GlobalLock.lock
    def get_inventory(self, context):
        """Return device structure with all standard attributes

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: response
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Autoload command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            snmp_handler = CgsSnmpHandler(resource_config, logger, api, cli_handler)

            autoload_operations = CgsAutoloadRunner(logger=logger,
                                                    resource_config=resource_config,
                                                    snmp_handler=snmp_handler)

            response = autoload_operations.discover()
            logger.info('Autoload command completed')

            return response

    @GlobalLock.lock
    def restore(self, context, cancellation_context, path, configuration_type, restore_method, vrf_management_name):
        """Restores a configuration file

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str path: The path to the configuration file, including the configuration file name.
        :param str restore_method: Determines whether the restore should append or override the current configuration.
        :param str configuration_type: Specify whether the file should update the startup or running config.
        :param str vrf_management_name: Optional. Virtual routing and Forwarding management name
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Restore command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            configuration_type = configuration_type or "running"
            restore_method = restore_method or "override"
            vrf_management_name = vrf_management_name or resource_config.vrf_management_name

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            configuration_operations = CgsConfigurationRunner(cli_handler=cli_handler,
                                                              logger=logger,
                                                              resource_config=resource_config,
                                                              api=api)

            configuration_operations.restore(path=path,
                                             restore_method=restore_method,
                                             configuration_type=configuration_type,
                                             vrf_management_name=vrf_management_name)

            logger.info("Restore command ended")

    def save(self, context, cancellation_context, folder_path, configuration_type, vrf_management_name):
        """Creates a configuration file and saves it to the provided destination

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str configuration_type: Specify whether the file should update the startup or running config. Value can one
        :param str folder_path: The path to the folder in which the configuration file will be saved.
        :param str vrf_management_name: Optional. Virtual routing and Forwarding management name
        :return The configuration file name.
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Save command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)
            configuration_type = configuration_type or "running"
            vrf_management_name = vrf_management_name or resource_config.vrf_management_name

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            configuration_operations = CgsConfigurationRunner(cli_handler=cli_handler,
                                                              logger=logger,
                                                              resource_config=resource_config,
                                                              api=api)

            response = configuration_operations.save(folder_path=folder_path, configuration_type=configuration_type,
                                                     vrf_management_name=vrf_management_name)

            logger.info('Save command ended with response: {}'.format(response))
            return response

    @GlobalLock.lock
    def load_firmware(self, context, cancellation_context, path, vrf_management_name):
        """Upload and updates firmware on the resource

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param str path: path to tftp server where firmware file is stored
        :param str vrf_management_name: Optional. Virtual routing and Forwarding management name
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Load firmware command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            vrf_management_name = vrf_management_name or resource_config.vrf_management_name

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            firmware_operations = CgsFirmwareRunner(cli_handler=cli_handler, logger=logger)
            response = firmware_operations.load_firmware(path=path, vrf_management_name=vrf_management_name)
            logger.info('Load firmware command ended with response: {}'.format(response))

    def run_custom_command(self, context, cancellation_context, custom_command):
        """Executes a custom command on the device

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str custom_command: The command to run. Note that commands that require a response are not supported.
        :return: the command result text
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Run Custom command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            send_command_operations = RunCommandRunner(logger=logger,
                                                       cli_handler=cli_handler)

            response = send_command_operations.run_custom_command(custom_command=parse_custom_commands(custom_command))
            logger.info('Run Custom command ended with response: {}'.format(response))

            return response

    def run_custom_config_command(self, context, cancellation_context, custom_command):
        """Executes a custom command on the device in configuration mode

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str custom_command: The command to run. Note that commands that require a response are not supported.
        :return: the command result text
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Run Custom Config command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)
            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            send_command_operations = RunCommandRunner(logger=logger,
                                                       cli_handler=cli_handler)

            response = send_command_operations.run_custom_config_command(
                custom_command=parse_custom_commands(custom_command))

            logger.info('Run Custom Config command ended with response: {}'.format(response))

            return response

    def shutdown(self, context, cancellation_context):
        """Sends a graceful shutdown to the device

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        """
        pass

    def orchestration_save(self, context, cancellation_context, mode, custom_params):
        """Saves the Shell state and returns a description of the saved artifacts and information

        This command is intended for API use only by sandbox orchestration scripts to implement
        a save and restore workflow
        :param ResourceCommandContext context: the context object containing resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
        :param str custom_params: Set of custom parameters for the save operation
        :return: SavedResults serialized as JSON
        :rtype: OrchestrationSaveResult
        """

        # See below an example implementation, here we use jsonpickle for serialization,
        # to use this sample, you'll need to add jsonpickle to your requirements.txt file
        # The JSON schema is defined at: https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
        # You can find more information and examples examples in the spec document at https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
        '''
        # By convention, all dates should be UTC
        created_date = datetime.datetime.utcnow()
        # This can be any unique identifier which can later be used to retrieve the artifact
        # such as filepath etc.
        # By convention, all dates should be UTC
        created_date = datetime.datetime.utcnow()
        # This can be any unique identifier which can later be used to retrieve the artifact
        # such as filepath etc.
        identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')
        orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)
        saved_artifacts_info = OrchestrationSavedArtifactInfo(
            resource_name="some_resource",
            created_date=created_date,
            restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
            saved_artifact=orchestration_saved_artifact)
        return OrchestrationSaveResult(saved_artifacts_info)
        '''
        pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """Restores a saved artifact previously saved by this Shell driver using the orchestration_save function

        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        pass

    def health_check(self, context):
        """Performs device health check

        :param ResourceCommandContext context: ResourceCommandContext object with all Resource Attributes inside
        :return: Success or Error message
        :rtype: str
        """
        logger = get_logger_with_thread_id(context)
        logger.info('Health Check command started')

        with ErrorHandlingContext(logger):
            api = get_api(context)

            resource_config = create_load_balancing_resource_from_context(shell_name=self.SHELL_NAME,
                                                                          supported_os=self.SUPPORTED_OS,
                                                                          context=context)

            cli_handler = CgsCliHandler(cli=self._cli,
                                        resource_config=resource_config,
                                        logger=logger,
                                        api=api)

            state_operations = CgsStateRunner(logger=logger,
                                              api=api,
                                              resource_config=resource_config,
                                              cli_handler=cli_handler)

            result = state_operations.health_check()
            logger.info('Health Check command ended with result: {}'.format(result))

            return result

    def cleanup(self):
        """Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass


if __name__ == "__main__":
    import json
    import mock
    from cloudshell.shell.core.driver_context import ResourceCommandContext, ResourceContextDetails, \
        ReservationContextDetails

    def prepare_context(address="192.168.85.14", user="admin", password="admin", port=6666):
        """
        :return:
        """
        """Return initialized driver instance"""
        context = ResourceCommandContext(*(None,) * 4)
        context.resource = ResourceContextDetails(*(None,) * 13)
        context.resource.name = "CGS COS Loadbalancer Shell 2G"
        context.resource.fullname = "CGS COS Loadbalancer Shell 2G"
        context.resource.address = address
        context.resource.family = "CS_Switch"
        context.reservation = ReservationContextDetails(*(None,) * 7)
        context.reservation.reservation_id = '0cc17f8c-75ba-495f-aeb5-df5f0f9a0e97'
        context.resource.attributes = {}

        for attr, value in [("User", user),
                            ("Sessions Concurrency Limit", 1),
                            ("CLI Connection Type", "SSH"),
                            ("Password", password),
                            ("Enable Password", password),
                            ("CLI TCP Port", port),

                            # Backup location attributes for the "Save" command
                            ("Backup Location", ""),
                            ("Backup Type", "File System"),
                            ("Backup User", "backup_user"),
                            ("Backup Password", "backup_pass"),

                            # SNMP v2 Read-only
                            ("SNMP Version", "2"),
                            ("Enable SNMP", "True"),
                            ("Disable SNMP", "True"),
                            ("SNMP Read Community", "public_testing_2"),
                            # End SNMP v2 Read-only

                            # SNMP v2 Read-Write
                            # ("SNMP Version", "2"),
                            # ("Enable SNMP", "True"),
                            # ("Disable SNMP", "False"),
                            # ("SNMP Write Community", "public_33"),
                            # End SNMP v2 Read-Write

                            # SNMP v3
                            # ("SNMP Version", "3"),
                            # ("Enable SNMP", "True"),
                            # ("Disable SNMP", "True"),
                            # ("SNMP V3 User", "quali_NEW_NEW2"),
                            # ("SNMP V3 Password", "qualipass"),
                            # ("SNMP V3 Private Key", "qualipass2"),
                            # ("SNMP V3 Authentication Protocol", "No Authentication Protocol"),
                            # "No Authentication Protocol", "MD5", "SHA"
                            ("SNMP V3 Privacy Protocol", "No Privacy Protocol"),
                            # "No Privacy Protocol", "DES", "3DES-EDE", "AES-128", "AES-192", "AES-256"
                            # End SNMP v3
                            ]:

            context.resource.attributes["{}.{}".format(CgsCosLoadbalancerShell2GDriver.SHELL_NAME, attr)] = value
            context.connectivity = mock.MagicMock()
            context.connectivity.server_address = "192.168.85.10"

        return context


    def get_driver(context):
        """
        :return:
        """
        dr = CgsCosLoadbalancerShell2GDriver()
        dr.initialize(context)
        return dr


    def get_inventory(driver, context):
        """
        :param driver:
        :return:
        """
        return [res.__dict__ for res in driver.get_inventory(context).resources]


    def health_check(driver, context):
        """
        :param driver:
        :return:
        """
        return driver.health_check(context)


    def shutdown(driver, context):
        """
        :param driver:
        :return:
        """
        return driver.shutdown(context, None)


    def run_custom_command(driver, context, custom_command="help"):
        """
        :param driver:
        :param context:
        :param custom_command:
        :return:
        """
        return driver.run_custom_command(context=context, cancellation_context=None, custom_command=custom_command)


    def run_custom_config_command(driver, context, custom_command="help"):
        """
        :param driver:
        :param context:
        :param custom_command:
        :return:
        """
        return driver.run_custom_config_command(context=context, cancellation_context=None,
                                                custom_command=custom_command)


    def save(driver, context, folder_path, configuration_type, vrf_management_name=""):
        """
        :param driver:
        :param context:
        :param folder_path:
        :param configuration_type:
        :param vrf_management_name:
        :return:
        """
        return driver.save(context=context,
                           cancellation_context=None,
                           folder_path=folder_path,
                           configuration_type=configuration_type,
                           vrf_management_name=vrf_management_name)


    def restore(driver, context, path, configuration_type, restore_method, vrf_management_name=""):
        """
        :param driver:
        :param context:
        :param path:
        :param configuration_type:
        :param restore_method:
        :param vrf_management_name:
        :return:
        """
        return driver.restore(context=context,
                              cancellation_context=None,
                              path=path,
                              configuration_type=configuration_type,
                              restore_method=restore_method,
                              vrf_management_name=vrf_management_name)


    def load_firmware(driver, context, path, vrf_management_name=""):
        """
        :param driver:
        :param context:
        :param path:
        :param vrf_management_name:
        :return:
        """
        return driver.load_firmware(context=context,
                                    cancellation_context=None,
                                    path=path,
                                    vrf_management_name=vrf_management_name)

    context = prepare_context(address="192.168.42.201")
    # context = prepare_context(address="192.168.85.14")
    dr = get_driver(context)

    with mock.patch("__main__.get_api") as aa:
        get_api.return_value.DecryptPassword = lambda x: mock.MagicMock(Value=x)

        # get inventory
        # print get_inventory(driver=dr, context=context)

        # health check
        # print health_check(driver=dr, context=context)
        #
        # # shutdown
        # print shutdown(driver=dr, context=context)
        #
        # run custom command
        # print run_custom_command(driver=dr, context=context)
        #
        # run custom config command
        # print run_custom_config_command(driver=dr, context=context)
        #
        # # run save command
        # print save(driver=dr,
        #            context=context,
        #            folder_path="",
        #            configuration_type="running",
        #            vrf_management_name="")

        # print save(driver=dr,
        #            context=context,
        #            folder_path="scp://quali:quali@192.168.85.13/home/quali",
        #            configuration_type="running",
        #            vrf_management_name="")
        #
        # print save(driver=dr,
        #            context=context,
        #            folder_path="ftp://dlpuser@dlptest.com:fLDScD4Ynth0p4OJ6bW6qCxjh@146.66.113.185",
        #            configuration_type="running",
        #            vrf_management_name="")
        #
        # print restore(driver=dr,
        #               context=context,
        #               path="ftp://dlpuser@dlptest.com:fLDScD4Ynth0p4OJ6bW6qCxjh@146.66.113.185/CGS-startup-160919-050102",
        #               configuration_type="running",
        #               restore_method="override",
        #               vrf_management_name="")
        # #
        # print restore(driver=dr,
        #               context=context,
        #               path="CGS_COS_Switch_Shell_2G-running-020919-153008",
        #               configuration_type="running",
        #               restore_method="override",
        #               vrf_management_name="")
        #
        # print load_firmware(driver=dr,
        #                     context=context,
        #                     path="ftp://cgs@192.168.201.100/NPB-II-x86-2.6.1.bin.tar")

        # print load_firmware(driver=dr,
        #                     context=context,
        #                     path="ftp://dlpuser@dlptest.com:fLDScD4Ynth0p4OJ6bW6qCxjh@146.66.113.185/CGS_COS_Switch_Shell_2G-running-020919-151037")
