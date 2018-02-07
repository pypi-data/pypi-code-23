import xldeploy
import pkg_resources
import platform
import traceback

from os import environ, path
from sys import argv
from xld.xld_args_validator import XldArgsValidator
from xld.help import help_message
from xld.help_deploy import deploy_usage
from xld.help_apply import apply_usage
from xld.utility import find_uploads, read_files
from xldeploy.errors import APIError, XLDeployAuthenticationError


class XldCommands:
    def __init__(self, url=None, username=None, password=None, debug=False):
        if self.__is_config_required(argv[0:]):
            self.__url = self.__get_arg_value(url, XldArgsValidator.XL_DEPLOY_URL)
            self.__username = self.__get_arg_value(username, XldArgsValidator.XL_DEPLOY_USERNAME)
            self.__password = self.__get_arg_value(password, XldArgsValidator.XL_DEPLOY_PASSWORD)
            self.__debug = debug

            XldArgsValidator().validate(self.__url, self.__username, self.__password)

            config = xldeploy.Config.initialize(url=self.__url + '/deployit',
                                                username=self.__username,
                                                password=self.__password)
            self.__client = xldeploy.Client(config)

    def __get_arg_value(self, param_value, env_variable):
        return environ.get(env_variable, None) if param_value is None else param_value

    def apply(self, file_path=None):
        if not file_path:
            return apply_usage.format(xld_url=self.__url, xld_username=self.__username, xld_password=self.__password)

        try:
            deploy_file = open(file_path, 'rb').read()
            matched_file = find_uploads(deploy_file)
            files_to_upload = read_files(matched_file, path.abspath(path.join(file_path, "..")))
            # print(files_to_upload)
            return self.__client.deployfile.apply(file_path, files_to_upload)
        except Exception as e:
            return self.__handle_error(e)

    def deploy(self, package_id=None, environment_id=None):
        if not package_id or not environment_id:
            return deploy_usage.format(xld_url=self.__url, xld_username=self.__username, xld_password=self.__password)

        try:
            deployment = self.__client.deployment
            # Start deployment
            deploymentRef = deployment.prepare_initial(package_id, environment_id)
            depl = deployment.prepare_auto_deployeds(deploymentRef)
            task = deployment.create_task(depl)
            task.start()
            return task.task_id
        except Exception as e:
            return self.__handle_error(e)

    def generate(self, *directories):
        try:
            return self.__client.deployfile.generate(list(directories))
        except Exception as e:
            return self.__handle_error(e)

    def help(self):
        return help_message

    def version(self):
        packagedir = path.abspath(path.join(__file__, "../"))
        version = "xld-py-cli %s from %s (python %s)" % (
            pkg_resources.get_distribution('xld-py-cli').version, packagedir, platform.python_version())
        return version

    def __is_config_required(self, args):
        return 'version' not in args and 'help' not in args

    def __handle_error(self, error):
        message = ""
        if isinstance(error, XLDeployAuthenticationError):
            message = "The username or password you have entered is incorrect."
        elif isinstance(error, APIError):
            if error.is_client_error():
                message = "Client Error:\n"
            elif error.is_server_error():
                message = "Server Error:\n"
            message += "\t %s" % error.explanation
        else:
            message = error.__str__()
        if self.__debug:
            traceback.print_stack()
        return message
