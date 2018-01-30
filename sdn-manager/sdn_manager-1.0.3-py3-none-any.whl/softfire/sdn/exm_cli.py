import json
from optparse import OptionParser

import grpc
import yaml
from sdk.softfire.grpc import messages_pb2_grpc, messages_pb2
from sdk.softfire.grpc.messages_pb2 import UserInfo
from sdk.softfire.utils import get_config


class ExManagerCli(object):
    def __init__(self, target=None) -> None:
        super().__init__()
        self._username = "invalid"
        self._password = "invalid"
        self._testbed_tenants = {messages_pb2.FOKUS_DEV: "654invalid321"}

        if target is None:
            target = '%s:%s' % (self.get_config_value("system", "ip", "localhost"),
                                self.get_config_value("messaging", "bind_port", "5051"))
        self._channel_to_manager = grpc.insecure_channel(target)

    def get_config_value(self, section, key, default=None, config_file_path="/etc/softfire/sdn-manager.ini"):
        return get_config(section=section, key=key, default=default, config_file_path=config_file_path)

    def get_user_info(self):
        result = messages_pb2.UserInfo()
        # result.id = ex.id
        result.name = self._username
        result.password = self._password
        result.ob_project_id = "0000"
        for k, v in self._testbed_tenants.items():
            result.testbed_tenants[k] = v
        return result

    def send_create_user_as_em(self):
        """
        rpc create_user (UserInfo) returns (UserInfo) { }
        :return:
        """

        stub = messages_pb2_grpc.ManagerAgentStub(channel=self._channel_to_manager)

        stub.create_user(self.get_user_info())

    def send_refresh_resources_as_em(self):
        """
        rpc refresh_resources (UserInfo) returns (ResponseMessage) { }
        :return:
        """

        stub = messages_pb2_grpc.ManagerAgentStub(channel=self._channel_to_manager)
        stub.refresh_resources(self.get_user_info())

    def send_execute_as_em(self, method, payload: str, user_info: UserInfo):
        """
        rpc execute (RequestMessage) returns (ResponseMessage) { }
        message RequestMessage {
            Method method: enum Method {
                                LIST_RESOURCES = 0;
                                PROVIDE_RESOURCES = 1;
                                RELEASE_RESOURCES = 2;
                                VALIDATE_RESOURCES = 3;
                            }
            string payload: json
            UserInfo user_info
        }
        :return:
        """
        stub = messages_pb2_grpc.ManagerAgentStub(channel=self._channel_to_manager)
        response = stub.execute(
            messages_pb2.RequestMessage(method=method, payload=payload, user_info=user_info))

        if response.result == messages_pb2.Ok:
            print("Result: OK")
            print("message: %s" % response)
        elif response.result == messages_pb2.ERROR:
            print("Result: Error msg: %s" % response.error_message)

    def send_validate_resources_as_em(self):
        #data = dict(SdnResource=dict(properties=dict(resource_id="sdn-controller-opensdncore-fokus")), derived_from="eu.softfire.BaseResource")
        data = {
            "properties": {
                "resource_id": "sdn-controller-opensdncore-fokus",
            },
            "type": "SdnResource"
        }
        yml = yaml.dump(data)
        print("dict: %s" % data)
        print("yaml: %s" % yml)
        self.send_execute_as_em(messages_pb2.VALIDATE_RESOURCES, yml, self.get_user_info())

    def send_provide_resources_as_em(self):
        data = {
            "properties": {
                "resource_id": "sdn-controller-opensdncore-fokus",
            },
            "type": "SdnResource"
        }
        self.send_execute_as_em(messages_pb2.PROVIDE_RESOURCES, json.dumps(data), self.get_user_info())

    def send_update_status_to_em(self):
        resources_per_experimenter = {}

        target = '%s:%s' % (self.get_config_value("system", "experiment_manager_ip", "localhost"),
                            self.get_config_value("system", "experiment_manager_port", "5051"))

        channel = grpc.insecure_channel(target)
        stub = messages_pb2_grpc.RegistrationServiceStub(channel=channel)
        manager_name = self.get_config_value('system', 'name')
        for username, resources in resources_per_experimenter.items():
            rpc_res = []
            for res in resources:
                rpc_res.append(messages_pb2.Resource(content=json.dumps(json.loads(res))))
            status_message = messages_pb2.StatusMessage(
                resources=rpc_res,
                username=username,
                manager_name=manager_name
            )
            stub.update_status(status_message)


def main():
    parser = OptionParser()
    # parser.add_option("-t", "--host", dest="hostname", action="store",
    #                  help="Hostname or IP of manager")
    # parser.add_option("-o", "--port", dest="port", action="store",
    #                  help="port number of manager")

    parser.add_option("-c", "--create_user", action="append_const", dest="methods", const="send_create_user_as_em",
                      help="send a create_user message to the manager")

    parser.add_option("-v", "--validate", action="append_const", dest="methods", const="send_validate_resources_as_em",
                      help="send a validate_resources message to the manager")

    parser.add_option("-p", "--provide", action="append_const", dest="methods", const="send_provide_resources_as_em",
                      help="send a provide_resources message to the manager")

    (options, args) = parser.parse_args()
    return options


def callmethod(cls, mtd_name):
    method = getattr(cls, mtd_name)
    method()


if __name__ == '__main__':
    # TODO parse arguments
    ex = ExManagerCli()
    # ex.send_create_user_as_em()
    options = main()
    if isinstance(options.methods,list):
        for method in options.methods:
            print("Invoking method: %s" % method)
            try:
                callmethod(ex, method)
            except Exception as e:
                print("Error: %s" % e)
    else:
        print("useage --help")
