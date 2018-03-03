import unittest

from tcell_agent.sanitize.passwords import fingerprint_password
from tcell_agent.config.configuration import CONFIGURATION


class PasswordsTest(unittest.TestCase):

    def none_password_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = "password_hmac_key"

        hashed_password = fingerprint_password(None, None)
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertIsNone(hashed_password)

    def empty_password_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = "password_hmac_key"

        hashed_password = fingerprint_password("", None)
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertIsNone(hashed_password)

    def blank_password_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = "password_hmac_key"

        hashed_password = fingerprint_password("   ", None)
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertIsNone(hashed_password)

    def none_password_hmac_key_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = None

        hashed_password = fingerprint_password("admin123", None)
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertIsNone(hashed_password)

    def none_user_id_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = "password_hmac_key"

        hashed_password = fingerprint_password("admin123", None)
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertEqual(hashed_password, "83ff14db")

    def present_user_id_fingerprint_password_test(self):
        orig_password_hmac_key = CONFIGURATION.password_hmac_key
        CONFIGURATION.password_hmac_key = "password_hmac_key"

        hashed_password = fingerprint_password("admin123", "user_id")
        CONFIGURATION.password_hmac_key = orig_password_hmac_key

        self.assertEqual(hashed_password, "11a88b27")
