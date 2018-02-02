from iceman.configuration import Configuration
from iceman.interceptor import Interceptor

def configuration():
    config = Configuration()
    strategy = config.CRYPTO_STRATEGIES[0]
    config.cipher_suite = config.initialize_cipher_suite(strategy)
    return config

