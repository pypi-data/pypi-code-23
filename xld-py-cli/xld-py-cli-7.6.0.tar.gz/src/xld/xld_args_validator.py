from __future__ import print_function
import sys
from fire import core
from fire import trace


class XldArgsValidator:

    __validation_error_msg = "Missing required parameter --{param} or Environment variable {env_variable}"
    XL_DEPLOY_URL = 'XL_DEPLOY_URL'
    XL_DEPLOY_USERNAME = 'XL_DEPLOY_USERNAME'
    XL_DEPLOY_PASSWORD = 'XL_DEPLOY_PASSWORD'

    def __init__(self):
        pass

    def validate(self, url, username, password):
        error_trace = trace.FireTrace(self, verbose=True, show_help=True, show_trace=True)
        self.__is_valid_value(url, 'url', self.XL_DEPLOY_URL, error_trace)
        self.__is_valid_value(username, 'username', self.XL_DEPLOY_USERNAME, error_trace)
        self.__is_valid_value(password, 'password', self.XL_DEPLOY_PASSWORD, error_trace)
        if error_trace.HasError():
            # log the error trace on console, as raising the Exception does not log it on its own.
            self.__print_validation_errors(error_trace)
            raise core.FireExit(2, error_trace)

    def __is_valid_value(self, param_value, param_name, env_variable, error_trace):
        if param_value is None:
            error_trace.AddError(
                core.FireError(self.__validation_error_msg.format(param=param_name, env_variable=env_variable)),
                sys.argv[1:])

    def __print_validation_errors(self, error_trace):
        error_message = 'Usage Error: \n' + '\n'.join(
            '{index}. {trace_string}'.format(index=index + 1, trace_string=element)
            for index, element in enumerate(error_trace.elements[1:]))
        print(error_message, file=sys.stderr)
