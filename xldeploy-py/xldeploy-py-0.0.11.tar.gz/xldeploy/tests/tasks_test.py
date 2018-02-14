from unittest import TestCase
import xldeploy
from xldeploy.domain.ConfigurationItem import ConfigurationItem
import sys
import time


class TasksTest(TestCase):
    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.tasks = client.tasks
        self.deployment = client.deployment
        self.repo = client.repository

    def get_deployment_object(self):
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
        depl = self.deployment.prepare_initial(package_ci.id, environment_ci.id)
        deployment = self.deployment.prepare_auto_deployeds(depl)
        return deployment

    def clean_up_cis(self):
        # Cleanup
        self.repo.delete("Environments/SampleEnv/Sample")
        self.repo.delete("Environments/SampleEnv")
        self.repo.delete("Infrastructure/localHost")
        self.repo.delete("Applications/Sample/1.0/commandCI")
        self.repo.delete("Applications/Sample/1.0")
        self.repo.delete("Applications/Sample")


    def test_get_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        actual_task = self.tasks.get_task(task.task_id)
        self.assertEqual(task.task_id , actual_task["id"])
        self.clean_up_cis()

    def test_get_steps(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        res = task.get_steps( "0_1_1")
        self.assertTrue(res["description"] in ["Deploy Sample 1.0 on environment SampleEnv", "Deploy Sample 1.0 on SampleEnv"])
        self.clean_up_cis()

    def test_start_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        task.start()

        running_task = self.tasks.get_task(task.task_id)
        self.assertEqual(running_task["state"], "EXECUTING")
        self.clean_up_cis()

    def test_stop_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        task.start()
        task.stop()

        running_task = self.tasks.get_task(task.task_id)
        self.assertTrue(running_task["state"] in ["EXECUTED", "STOPPED", "STOPPING"])
        self.clean_up_cis()

    def test_abort_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        task.start()
        task.abort()
        status = None
        while status != "ABORTED":
            running_task = task.get_task()
            status = running_task["state"]
        running_task = self.tasks.get_task(task.task_id)
        self.assertEqual(running_task["state"], "ABORTED")
        self.clean_up_cis()

    def test_cancel_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        task.start()
        task.abort()

        task.cancel()
        # time.sleep(2)
        running_task = self.tasks.get_task(task.task_id)
        self.assertTrue(running_task["state"] in ["ABORTED", "CANCELLED"])
        self.clean_up_cis()

    def test_archive_task(self):
        deployment = self.get_deployment_object()
        task = self.deployment.create_task(deployment)
        task.start()
        status = None
        while status != "EXECUTED":
            running_task = task.get_task()
            status = running_task["state"]

        task.archive(task)
        running_task = self.tasks.get_task(task.task_id)
        self.assertEqual(running_task["state"], "DONE")
        self.clean_up_cis()