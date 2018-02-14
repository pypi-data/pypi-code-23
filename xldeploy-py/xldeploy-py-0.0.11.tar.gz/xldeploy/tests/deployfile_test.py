from unittest import TestCase
import os
import xldeploy
from xldeploy.domain.ConfigurationItem import ConfigurationItem


class DeployfileTest(TestCase):
    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.deployfile = client.deployfile
        self.repo = client.repository
        self.clean_up_cis()

    def clean_up_cis(self):
        # Cleanup
        self.repo.delete("Environments/DEV")
        self.repo.delete("Infrastructure/localHost")

    def generate_deployfile_test(self):
        localhost = ConfigurationItem("Infrastructure/localHost", "overthere.LocalHost", {"os": "UNIX"})
        self.repo.create_ci(localhost)
        directory_ci = ConfigurationItem("Environments/DEV", "core.Directory")
        self.repo.create_ci(directory_ci)
        environment_ci = ConfigurationItem("Environments/DEV/SampleEnv", "udm.Environment", {'members': [localhost.id]})
        self.repo.create_ci(environment_ci)

        generated_deployfile = self.deployfile.generate(['Environments/DEV'])
        expected_deployfile = open(os.path.join(os.path.dirname(__file__), 'test_deployfile.txt'), 'r').read()
        self.assertEqual(generated_deployfile, expected_deployfile)
        self.clean_up_cis()

    def apply_deployfile_test(self):
        localhost = ConfigurationItem("Infrastructure/localHost", "overthere.LocalHost", {"os": "UNIX"})
        self.repo.create_ci(localhost)
        deployfile_to_apply = open(os.path.join(os.path.dirname(__file__), 'test_deployfile.txt'), 'r').read()
        self.deployfile.apply(deployfile_to_apply, [])
        self.assertTrue(self.repo.exists("Environments/DEV/SampleEnv"))
        self.clean_up_cis()
