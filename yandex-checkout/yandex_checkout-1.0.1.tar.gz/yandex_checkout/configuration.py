class ConfigurationError(Exception):
    pass


class Configuration(object):
    """
    A class representing the configuration.
    """
    api_url = "https://payment.yandex.net/api/v3"
    account_id = None
    secret_key = None
    timeout = 1800
    max_attempts = 3

    def __init__(self, **kwargs):
        self.assert_has_api_credentials()

    @staticmethod
    def configure(account_id, secret_key, **kwargs):
        Configuration.account_id = account_id
        Configuration.secret_key = secret_key
        Configuration.timeout = kwargs.get("timeout", 1800)
        Configuration.max_attempts = kwargs.get("max_attempts", 3)

    @staticmethod
    def instantiate():
        return Configuration(
            shop_id=Configuration.account_id,
            shop_password=Configuration.secret_key,
            timeout=Configuration.timeout,
            max_attempts=Configuration.max_attempts,
        )

    @staticmethod
    def api_endpoint():
        return Configuration.api_url

    def has_api_credentials(self):
        return self.account_id is not None and self.secret_key is not None

    def assert_has_api_credentials(self):
        if not self.has_api_credentials():
            raise ConfigurationError("account_id and secret_key are required")
