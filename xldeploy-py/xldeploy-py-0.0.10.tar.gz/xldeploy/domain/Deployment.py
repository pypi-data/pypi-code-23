import json


class Deployment(object):

    @staticmethod
    def as_deployment(json_data):
        required_deployments = None
        deployment_group_index = None
        pjson = json.loads(json_data)
        if 'requiredDeployments' in pjson:
            required_deployments = pjson['requiredDeployments']
        if 'deploymentGroupIndex' in pjson:
            deployment_group_index = pjson['deploymentGroupIndex']
        deployment = Deployment(pjson['id'], pjson['application'], pjson['deployeds'], pjson['deployables'],
                                pjson['containers'], required_deployments, deployment_group_index,
                                pjson['type'])
        return deployment

    def __init__(self, id, application, deployeds, deployables, containers, requiredDeployments,
                 deploymentGroupIndex, type):
        self.id = id
        self.application = application
        self.deployeds = deployeds
        self.deployables = deployables
        self.containers = containers
        self.requiredDeployments = requiredDeployments
        self.deploymentGroupIndex = deploymentGroupIndex
        self.type = type

    def to_dict(self):
        return dict(id=self.id, application=self.application, deployeds=self.deployeds, deployables=self.deployables,
                    containers=self.containers, requiredDeployments=self.requiredDeployments,
                    deploymentGroupIndex=self.deploymentGroupIndex, type=self.type)

