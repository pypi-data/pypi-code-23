""" Tests for seed_services_cli.identity_store """

from unittest import TestCase
from click.testing import CliRunner
from seed_services_cli.main import cli
import responses


class TestSendCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def invoke_user_tokens_generate(self, args, user=2, email="a@b.org"):
        return self.runner.invoke(cli, [
            'ci-user-token-generate',
            '--user', user,
            '--email', email,
        ] + args)

    def test_user_tokens_generate_help(self):
        result = self.runner.invoke(cli, ['ci-user-token-generate', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Trigger generation of a users service tokens"
            in result.output)

    @responses.activate
    def test_user_tokens_generate_no_details(self):
        # setup
        result = self.runner.invoke(cli, ['ci-user-token-generate'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Please specify all user information. See --help."
            in result.output)

    @responses.activate
    def test_user_tokens_generate(self):
        # setup

        ust_response = {
            "user_service_token_initiated": True,
            "count": 2
        }
        responses.add(responses.POST,
                      "http://ci-svc.example.org/api/v1/userservicetoken/generate/",  # noqa
                      json=ust_response, status=201)

        # Execute
        result = self.invoke_user_tokens_generate([])
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Triggering token creation for a@b.org"
                        in result.output)
        self.assertTrue("Triggered generation of 2 tokens" in result.output)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url,
                         "http://ci-svc.example.org/api/v1/userservicetoken/generate/")  # noqa

    def test_get_service_status_help(self):
        result = self.runner.invoke(cli, ['ci-status', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Get service status"
            in result.output)

    @responses.activate
    def test_get_service_status(self):
        # setup
        services_response = {
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "ba79f008-cc34-437e-ba6a-02b3c2e5fc9e",
                    "name": "SEED_IDENTITY_STORE",
                    "url": "http://id.seed.example.org",
                    "token": "id_store_token",
                    "up": True,
                    "metadata": None,
                    "created_at": "2016-05-05T14:06:33.250602Z",
                    "created_by": 1,
                    "updated_at": "2016-05-05T14:06:33.250630Z",
                    "updated_by": 1
                },
                {
                    "id": "df7f3f44-aed1-4e75-a1f9-b6398ef4760e",
                    "name": "SEED_STAGE_BASED_MESSAGING",
                    "url": "http://sbm.seed.example.org",
                    "token": "sbm_store_token",
                    "up": False,
                    "metadata": None,
                    "created_at": "2016-08-03T13:12:18.296637Z",
                    "created_by": 1,
                    "updated_at": "2016-08-03T13:12:18.296794Z",
                    "updated_by": 1
                }
            ]
        }
        responses.add(responses.GET,
                      "http://ci-svc.example.org/api/v1/service/",
                      json=services_response, status=200)
        # Execute
        result = self.runner.invoke(cli, ['ci-status'])
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Getting all service status"
                        in result.output)
        self.assertTrue("Service SEED_IDENTITY_STORE is up. Last check: 2016-05-05T14:06:33.250630Z" in result.output)  # noqa
        self.assertTrue("Service SEED_STAGE_BASED_MESSAGING is down. Last check: 2016-08-03T13:12:18.296794Z" in result.output)  # noqa
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url,
                         "http://ci-svc.example.org/api/v1/service/")
