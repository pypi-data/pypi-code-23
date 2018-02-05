from xldeploy.domain.Deployment import Deployment
from xldeploy.domain.Task import Task
import json

class DeploymentService:

    __path = "/deployment"

    def __init__(self, http_client):
        self.http_client = http_client

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def is_deployed(self, application_id, environment_id):
        params = {"application": application_id, "environment": environment_id}
        response = self.http_client.get(path=self.get_path("exists"), params=params)
        return response.get("boolean")

    def prepare_initial(self, version_id, environment_id):
        params = {"version": version_id, "environment": environment_id}
        response = self.http_client.get(path=self.get_path("prepare", "initial"), params=params)
        deployment = Deployment.as_deployment(response)
        return deployment

    def prepare_update(self, version_id, deployed_application_id):
        params = {"version": version_id, "deployedApplication": deployed_application_id}
        response = self.http_client.get(path=self.get_path("prepare", "update"), params=params)
        deployment = Deployment.as_deployment(response)
        return deployment

    def prepare_undeploy(self, deployed_application_id):
        params = {"deployedApplication": deployed_application_id}
        response = self.http_client.get(path=self.get_path("prepare", "undeploy"), params=params)
        deployment = Deployment.as_deployment(response)
        return deployment

    def prepare_auto_deployeds(self, deployment):
        json_data = deployment.to_dict()
        response = self.http_client.post(path=self.get_path("prepare", "deployeds"), body=json_data)
        deployment = Deployment.as_deployment(response)
        return deployment

    def generate_selected_deployeds(self, deployable_ids, deployment):
        json_data = deployment.to_dict()
        params = {"deployables": deployable_ids}
        response = self.http_client.post(path=self.get_path("generate", "selected"), params=params, body=json_data)
        deployment = Deployment.as_deployment(response)
        return deployment

    def generate_single_deployed(self, deployable_id, container_id, deployed_type, deployment):
        json_data = deployment.to_dict()
        params = {"deployable": deployable_id, "container": container_id, "deployedtype": deployed_type}
        response = self.http_client.post(path=self.get_path("generate", "single"), params=params, body=json_data)
        deployment = Deployment.as_deployment(response)
        return deployment

    def validate(self, deployment):
        json_data = deployment.to_dict()
        response = self.http_client.post(path=self.get_path("validate"), body=json_data)
        deployment = Deployment.as_deployment(response)
        return deployment

    def create_task(self, deployment):
        json_data = deployment.to_dict()
        response = json.loads(self.http_client.post(path=self.get_path(), body=json_data))
        return Task(response["string"], self.http_client)

    def rollback(self, task_id):
        response = self.http_client.post(path=self.get_path("rollback", task_id))
        return Task(response["string"], self.http_client)

    def effective_dictionary(self, environment, application=None, container=None):
        params = {"environment": environment, "application": application, "container": container}
        response = self.http_client.get(path=self.get_path("dictionary"), params=params)
        return response

    def task_preview_block(self, deployment):
        raise Exception('Not implemented.')

    def task_preview_block(self, deployment, block_id, step_nr):
        raise Exception('Not implemented.')