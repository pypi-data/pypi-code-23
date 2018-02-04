import os
from localstack.services.infra import register_plugin, Plugin
from localstack.services.apigateway import apigateway_listener
from localstack_ext import config as config_ext
from localstack_ext.bootstrap import licensing, cli


# register default plugins

def register_localstack_plugins():

    # read license and prepare environment
    with licensing.prepare_environment():
        try:
            from localstack_ext.services.cognito import cognito_starter
            from localstack_ext.services.cognito import cognito_idp_api
            from localstack_ext.services.iam import iam_starter
            from localstack_ext.services.sts import sts_starter
            from localstack_ext.services import edge
            from localstack_ext.services import dns_server
            from localstack_ext.utils import auth
            from localstack_ext.utils import github_utils
        except Exception as e:
            return

    # Prepare network interfaces for DNS server and edge gateway. NOTE: This call
    # needs to remain here because it is also required when running LocalStack in Docker
    dns_server.setup_network_configuration()

    # add interceptors to all relevant APIs
    apigateway_listener.UPDATE_APIGATEWAY.forward_request = cognito_idp_api.wrap_api_method(
        'apigateway', apigateway_listener.UPDATE_APIGATEWAY.forward_request)

    # register_plugin(Plugin('ec2', start=ec2_starter.start_ec2))
    register_plugin(Plugin('sts', start=sts_starter.start_sts))
    register_plugin(Plugin('iam', start=iam_starter.start_iam))
    register_plugin(Plugin('cognito-idp', start=cognito_starter.start_cognito_idp))
    register_plugin(Plugin('cognito-identity', start=cognito_starter.start_cognito_identity))
    register_plugin(Plugin('edge', start=edge.start_edge))

    result = {
        'docker': {
            'run_flags': ('-p {dns_addr}:{dns_port}:{dns_port} -p {dns_addr}:{dns_port}:{dns_port}/udp'.
                format(dns_addr=config_ext.DNS_ADDRESS, dns_port=dns_server.DNS_PORT))
        }
    }
    return result


def register_localstack_commands():
    # only register CLI commands if a license key is configured
    if os.environ.get('LICENSE_KEY'):
        cli.register_commands()
    return True
