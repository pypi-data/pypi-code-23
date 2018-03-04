import os
import tempfile
import re

from scp import SCPClient
from xml.etree import ElementTree
from cloudshell.traffic.teravm.cli import ctrl_command_templates
from cloudshell.cli.command_template.command_template_executor import CommandTemplateExecutor
from cloudshell.traffic.teravm import exceptions

from cloudshell.traffic.teravm.controller import constants


class TeraVMLoadConfigurationFlow(object):
    def __init__(self, cli_handler, resource_config, cs_api, reservation_id, logger):
        """

        :param traffic.teravm.cli.ctrl_handler.TeraVMControllerCliHandler cli_handler:
        :param traffic.teravm.controller.configuration_attributes_structure.TrafficGeneratorControllerResource resource_config:
        :param str reservation_id:
        :param logging.Logger logger:
        """
        self._cli_handler = cli_handler
        self._resource_config = resource_config
        self._cs_api = cs_api
        self._reservation_id = reservation_id
        self._logger = logger

    def _get_ports_from_reservation(self):
        """Get connected TeraVM ports from the reservation

        :rtype: dict[str, str]
        """
        ports = {}
        resources = self._cs_api.GetReservationDetails(reservationId=self._reservation_id).ReservationDescription.Resources
        port_pattern = r'{}/M(?P<module>\d+)/P(?P<port>\d+)'.format(self._resource_config.address)

        for resource in resources:
            if resource.ResourceModelName == constants.PORT_MODEL_2G:
                logical_name_attr = constants.PORT_LOGICAL_NAME_ATTR_2G
            elif resource.ResourceModelName == constants.PORT_MODEL_1G:
                logical_name_attr = constants.PORT_LOGICAL_NAME_ATTR_1G
            else:
                continue

            result = re.search(port_pattern, resource.FullAddress)

            if result:
                logical_name = self._cs_api.GetAttributeValue(resourceFullPath=resource.Name,
                                                              attributeName=logical_name_attr).Value
                if logical_name:
                    interface_id = "/".join([result.group('module'),
                                             constants.TEST_AGENT_NUMBER,
                                             result.group('port')])

                    ports[logical_name] = interface_id
        return ports

    def execute_flow(self, file_path):
        """

        :param str file_path: filename or full path to file
        :return:
        """
        available_ports = self._get_ports_from_reservation()

        file_path = self._get_test_file_path(file_path)
        temp_file_path = self._prepare_temp_test_file(file_path=file_path,
                                                      available_ports=available_ports)

        test_group_file = constants.TEST_GROUP_FILE.format(self._resource_config.test_user)

        with self._cli_handler.get_cli_service(self._cli_handler.default_mode) as session:
            scp = SCPClient(session.session._handler.get_transport())

            scp.put(temp_file_path, test_group_file)

            with session.enter_mode(self._cli_handler.cli_mode) as cli_session:
                try:
                    command = CommandTemplateExecutor(cli_service=cli_session,
                                                      command_template=ctrl_command_templates.DELETE_TEST_GROUP)

                    command.execute_command(test_group_name=constants.TEST_GROUP_NAME,
                                            user=self._resource_config.test_user)

                except exceptions.TestGroupDoesNotExist:
                    pass

                command = CommandTemplateExecutor(cli_service=cli_session,
                                                  command_template=ctrl_command_templates.IMPORT_TEST_GROUP)

                command.execute_command(test_group_file=test_group_file, user=self._resource_config.test_user)

            command = CommandTemplateExecutor(cli_service=cli_session,
                                              command_template=ctrl_command_templates.REMOVE_FILE)

            command.execute_command(file_name=test_group_file)

    def _get_test_file_path(self, file_path):
        """Get full file path for test config

        :param str file_path: filename or full path to file
        :rtype: str
        """
        for path in (os.path.join(self._resource_config.test_files_location, file_path),
                     os.path.join(self._resource_config.test_files_location, self._reservation_id, file_path),
                     file_path):

            if os.path.exists(path):
                return path

        raise exceptions.TeraVMException('File {} does not exists or "Test Files Location" attribute '
                                         'was not specified'.format(file_path))

    def _prepare_temp_test_file(self, file_path, available_ports):
        """Create test file in the temp directory and return its full path

        :param str file_path:
        :rtype: str
        """
        tree = ElementTree.parse(file_path)
        root = tree.getroot()
        name = root.find('./test_group/name')
        name.text = constants.TEST_GROUP_NAME

        missing_ports = []

        for virtual_host in root.findall('.//direct_virtual_host'):
            virtual_host_name = virtual_host.find('name').text.strip()
            interface = virtual_host.find('.//interface')

            if interface is not None:
                if virtual_host_name in available_ports:
                    interface.text = available_ports.pop(virtual_host_name)
                else:
                    missing_ports.append(virtual_host_name)

        if missing_ports:
            raise Exception('Ports with logical names {} are not present in the reservation'.format(missing_ports))

        temp_file_path = tempfile.mktemp()
        tree.write(temp_file_path)

        return temp_file_path
