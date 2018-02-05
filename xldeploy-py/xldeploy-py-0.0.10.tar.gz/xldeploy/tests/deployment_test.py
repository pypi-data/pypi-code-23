from unittest import TestCase
from xldeploy.domain.Deployment import Deployment
import xldeploy
from xldeploy.domain.ConfigurationItem import ConfigurationItem
from xldeploy.errors import  XLDeployException, APIError

class DeploymentTest(TestCase):


    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.tasks = client.tasks
        self.deployment = client.deployment
        self.repo = client.repository

    def get_deployables(self):
        self.clean_up_cis()
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_ci = self.repo.create_ci(ci)
        package_ci = ConfigurationItem("Applications/Sample/1.0", "udm.DeploymentPackage")
        package = self.repo.create_ci(package_ci)
        properties = {"commandLine": "sleep 5"}
        cmd_ci = ConfigurationItem("Applications/Sample/1.0/commandCI", "cmd.Command", properties)
        cmd_created_ci = self.repo.create_ci(cmd_ci)

        localhost = ConfigurationItem("Infrastructure/localHost", "overthere.LocalHost", { "os": "UNIX" })
        container_ci = self.repo.create_ci(localhost)
        environment_ci = ConfigurationItem("Environments/SampleEnv", "udm.Environment", {'members': [localhost.id]})
        environment = self.repo.create_ci(environment_ci)

        return {"package_id": package_ci.id, "environment_id": environment_ci.id}

    def clean_up_cis(self):
        # Cleanup
        self.repo.delete("Environments/SampleEnv/Sample")
        self.repo.delete("Environments/SampleEnv")
        self.repo.delete("Infrastructure/localHost")
        self.repo.delete("Applications/Sample/1.0/commandCI")
        self.repo.delete("Applications/Sample/1.0")
        self.repo.delete("Applications/Sample")

    def execute_first_deployment(self):
        deployables = self.get_deployables()
        depl = self.deployment.prepare_initial(deployables['package_id'], deployables['environment_id'])
        deployment = self.deployment.prepare_auto_deployeds(depl)
        task = self.deployment.create_task(deployment)
        task.start()
        status = None
        while status != "EXECUTED":
            running_task = task.get_task()
            status = running_task["state"]
        return {"deployment": deployment, "task": task}

    def is_deployed_test(self):
        deployment = self.execute_first_deployment()["deployment"]
        self.assertTrue(self.deployment.is_deployed("Applications/Sample", "Environments/SampleEnv"))
        self.clean_up_cis()

    def prepare_initial_test(self):
        deployables = self.get_deployables()
        depl = self.deployment.prepare_initial(deployables['package_id'], deployables['environment_id'])
        self.assertTrue(type(depl) is Deployment)
        self.clean_up_cis()

    def prepare_auto_deployeds_test(self):
        deployables = self.get_deployables()
        depl = self.deployment.prepare_initial(deployables['package_id'], deployables['environment_id'])
        deployment = self.deployment.prepare_auto_deployeds(depl)
        self.assertTrue(type(deployment) is Deployment)
        self.clean_up_cis()

    def prepare_undeploy_test(self):
        deployment = self.execute_first_deployment()["deployment"]
        undeploy_obj = self.deployment.prepare_undeploy("Environments/SampleEnv/Sample")
        self.assertTrue(type(undeploy_obj) is Deployment)
        self.clean_up_cis()

    def prepare_update_test(self):
        deployment = self.execute_first_deployment()["deployment"]
        update_deployment = self.deployment.prepare_auto_deployeds(deployment)
        self.assertTrue(type(update_deployment) is Deployment)
        self.clean_up_cis()

    def validate_test(self):
        deployment = self.execute_first_deployment()["deployment"]
        valid_deployment = self.deployment.validate(deployment)
        self.assertTrue(type(valid_deployment) is Deployment)
        self.clean_up_cis()

    def create_task_test(self):
        deployables = self.get_deployables()
        depl = self.deployment.prepare_initial(deployables['package_id'], deployables['environment_id'])
        deployment = self.deployment.prepare_auto_deployeds(depl)
        task = self.deployment.create_task(deployment)
        self.assertTrue(task is not None)
        self.clean_up_cis()

    def rollback_test(self):
        task = self.execute_first_deployment()["task"]
        rollback_task = self.deployment.rollback(task.task_id)
        self.assertTrue(rollback_task is not None)
        self.clean_up_cis()

    def should_throw_api_error_test(self):
        self.assertRaises(APIError, self.deployment.prepare_initial, "dummy-package", "dummy-env")

    def should_throw_xldeploy_exception_test(self):
        invalid_config = xldeploy.Config( protocol="http", host="localhost", port="4516", context_path="deployit", username="invalid", password="invalid")
        new_client = xldeploy.Client(invalid_config)
        self.assertRaises(XLDeployException, new_client.deployment.prepare_initial, "dummy-package", "dummy-env")