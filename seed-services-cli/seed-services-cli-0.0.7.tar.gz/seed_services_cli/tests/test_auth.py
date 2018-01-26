""" Tests for seed_services_cli.identity_store """

from unittest import TestCase
from click.testing import CliRunner
from seed_services_cli.main import cli
import responses
import json


class TestSendCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def invoke_user_add(self, args, first_name="First", last_name="Last",
                        email="test@example.com", password="pass",
                        admin=False):
        if admin:
            args = args + ["--admin"]
        return self.runner.invoke(cli, [
            'auth-user-add',
            '--first_name', first_name,
            '--last_name', last_name,
            '--email', email,
            '--password', password,
        ] + args)

    def invoke_user_change_password(self, args, email, password):
        return self.runner.invoke(cli, [
            'auth-user-change-password',
            '--email', email,
            '--password', password,
        ] + args)

    def invoke_user_add_team(self, args, user=2, team=3):
        return self.runner.invoke(cli, [
            'auth-user-add-team',
            '--user', user,
            '--team', team,
        ] + args)

    def test_user_add_help(self):
        result = self.runner.invoke(cli, ['auth-user-add', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Create a user"
            in result.output)

    @responses.activate
    def test_user_add_no_details(self):
        # setup
        login_response = {
            "token": "3e6de6f2cace86d3ac22d0a58e652f4b283ab58c"
        }
        responses.add(responses.POST,
                      "http://auth.example.org/user/tokens/",
                      json=login_response, status=201)
        result = self.runner.invoke(cli, ['auth-user-add'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Please specify all new user information. See --help."
            in result.output)

    @responses.activate
    def test_user_add(self):
        # setup
        login_response = {
            "token": "3e6de6f2cace86d3ac22d0a58e652f4b283ab58c"
        }
        responses.add(responses.POST,
                      "http://auth.example.org/user/tokens/",
                      json=login_response, status=201)

        user_response = {
            "id": "3",
            "url": "http://auth.example.org/users/9/",
            "first_name": "First",
            "last_name": "Last",
            "email": "test@example.com",
            "admin": False,
            "teams": [],
            "organizations": [],
            "active": False
        }
        responses.add(responses.POST,
                      "http://auth.example.org/users/",
                      json=user_response, status=200)
        # Execute
        result = self.invoke_user_add([])
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Creating account for test@example.com"
                        in result.output)
        self.assertTrue("Created user. ID is 3." in result.output)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.url,
                         "http://auth.example.org/users/")

    @responses.activate
    def test_user_add_admin(self):
        # setup
        login_response = {
            "token": "3e6de6f2cace86d3ac22d0a58e652f4b283ab58c"
        }
        responses.add(responses.POST,
                      "http://auth.example.org/user/tokens/",
                      json=login_response, status=201)

        user_response = {
            "id": "3",
            "url": "http://auth.example.org/users/9/",
            "first_name": "First",
            "last_name": "Last",
            "email": "test@example.com",
            "admin": False,
            "teams": [],
            "organizations": [],
            "active": True
        }
        responses.add(responses.POST,
                      "http://auth.example.org/users/",
                      json=user_response, status=200)
        # Execute
        result = self.invoke_user_add([], admin=True)
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Creating account for test@example.com"
                        in result.output)
        self.assertTrue("Created user. ID is 3." in result.output)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.url,
                         "http://auth.example.org/users/")

    @responses.activate
    def test_user_change_password(self):
        login_response = {
            "token": "3e6de6f2cace86d3ac22d0a58e652f4b283ab58c"
        }
        responses.add(responses.POST,
                      "http://auth.example.org/user/tokens/",
                      json=login_response, status=201)

        users_response = [{
            'email': 'test@example.org',
            }, {
            'id': 2,
            'email': 'test2@example.org'
            }]
        responses.add(responses.GET,
                      "http://auth.example.org/users/",
                      json=users_response, status=200)

        responses.add(responses.PUT,
                      "http://auth.example.org/users/2/",
                      json={}, status=200)

        result = self.invoke_user_change_password(
            [], email='test2@example.org', password='testpass')
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            'Changing password for test2@example.org' in result.output)
        self.assertEqual(len(responses.calls), 3)
        self.assertEqual(
            json.loads(responses.calls[2].request.body)['password'],
            'testpass')

    def test_user_add_team_help(self):
        result = self.runner.invoke(cli, ['auth-user-add-team', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Add a user to a team"
            in result.output)

    @responses.activate
    def test_user_add_user_team_no_details(self):
        # setup
        login_response = {
            "token": "3e6de6f2cace86d3ac22d0a58e652f4b283ab58c"
        }
        responses.add(responses.POST,
                      "http://auth.example.org/user/tokens/",
                      json=login_response, status=201)
        result = self.runner.invoke(cli, ['auth-user-add-team'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Please specify user and team. See --help."
            in result.output)
