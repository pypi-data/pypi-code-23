import os

from python_agent.common.constants import PREFIX, MESSAGES_CANNOT_BE_NONE


class EnvironmentVariablesResolver(object):
    """
    This class resolves Sealights Related environment variables.
    """
    def __init__(self, target_object):
        if (target_object == None):
            raise Exception("'target_object'" + MESSAGES_CANNOT_BE_NONE)

        self.key_to_case_sensitive_key = {}
        self.prefix_length = len(PREFIX)
        self.prefix = PREFIX.lower()

        keys = dir(target_object)
        for case_sensitive_key in keys:
            # Windows have upper case keys, so we keep a mapping between upper key (ie, 'APPNAME') to case sensitive one (ie, 'appName').
            self.key_to_case_sensitive_key[case_sensitive_key.upper()] = case_sensitive_key

    def resolve(self):
        result = {}
        for key in os.environ.keys():
            if key.lower().startswith(self.prefix):
                value = os.environ[key]
                uppercase_key = key[self.prefix_length:].upper()
                case_sensitive_key = self.key_to_case_sensitive_key[uppercase_key]
                # Update the underlying dictionary. We assume object use the case senstive keys
                result.update({case_sensitive_key: value})
        return result
