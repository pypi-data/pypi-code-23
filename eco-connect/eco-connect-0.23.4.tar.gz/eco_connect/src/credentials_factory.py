import os


class CredentialsFactory:

    @classmethod
    def get_env_var(cls, variable):
        return os.environ.get(variable, None)

    @classmethod
    def get_eco_credentials(cls):
        return (cls.get_env_var('ECO_CONNECT_USER'),
                cls.get_env_var('ECO_CONNECT_PASSWORD'))
