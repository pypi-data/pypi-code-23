import unittest
import os
from gfb.configuration import Config, SetupHelper
from gfb.configuration import MissingConfigError, InvalidConfigError


class TestConfig(unittest.TestCase):

    def test_missing_configuration(self):
        c = Config()
        try:
            c.read_configuration("missing.cfg")
        except MissingConfigError as error:
            self.assertIsInstance(error, MissingConfigError)

    def test_configfiles(self):
        exists = os.path.exists("good.ini")
        self.assertTrue(exists)
        exists = os.path.exists("bad.ini")
        self.assertTrue(exists)

    def test_good_configuration(self):
        c = Config()
        try:
            c.read_configuration("good.ini")
        except:
            self.fail
        self.assertEqual(c.username, 'barnardn@gmail.com')
        self.assertEqual(c.password, 'cheeba')
        self.assertEqual(c.api_key, 'testkey')

    def test_bad_configuration(self):
        c = Config()
        try:
            c.read_configuration("bad.ini")
        except InvalidConfigError as error:
            self.assertIsInstance(error, InvalidConfigError)


class TestSetupHelper(unittest.TestCase):
    """ tests the setup helperclass """
    def test_A_should_create(self):
        helper = SetupHelper()
        cont = helper.should_create_configuration("\nAnswer Y")
        self.assertTrue(cont)
        cont = helper.should_create_configuration("\nAnswer N")
        self.assertFalse(cont)

    def test_B_create_configuration(self):
        """ creates a configuration file user uname/pass """
        print("\n*** For this test: enter 'user' for username and 'pass' for password")
        path = os.path.expanduser("~/.gfbrc-unit-test")
        helper = SetupHelper(path)

        c = helper.setup_walkthrough()
        c.api_key = "apikey"
        c.save(path)
        self.assertEqual(c.username, 'user')
        self.assertEqual(c.password, 'pass')
        exists = os.path.exists(path)
        self.assertTrue(exists)
        statinfo = os.stat(path)
        file_mode = str(oct(statinfo.st_mode))[-3:]
        self.assertEqual(file_mode, '600', 'bad chmod')

    def test_C_read_configuration(self):
        """ tests reading the config file created in test B """
        c = Config()
        path = os.path.expanduser("~/.gfbrc-unit-test")
        try:
            c.read_configuration(path)
        except:
            self.fail
        self.assertEqual(c.username, 'user')
        self.assertEqual(c.password, 'pass')
        self.assertEqual(c.api_key, "apikey")
        os.unlink(path)

    def test_D_credentials_ckeck(self):
        """ test the setup helper credentials checker """
        path = os.path.expanduser("~/.gfbrc-unit-test")
        helper = SetupHelper(path)
        print("\n**** For this test, enter valid login credentials\n")
        c = helper.setup_walkthrough()
        result = helper.check_configuration(c)
        self.assertTrue(result)

    def test_E_bad_credentials(self):
        """ invalid credentials test"""
        path = os.path.expanduser("~/.gfbrc-unit-test")
        helper = SetupHelper(path)
        print("**** For this test, enter INVALID login credentials\n")
        c = helper.setup_walkthrough()
        result = helper.check_configuration(c)
        self.assertFalse(result)
