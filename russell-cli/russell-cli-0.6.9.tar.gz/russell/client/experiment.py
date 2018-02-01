import json

from russell.cli.utils import force_unicode
from russell.client.base import RussellHttpClient
from russell.manager.experiment_config import ExperimentConfigManager
from russell.model.experiment import Experiment

class ExperimentClient(RussellHttpClient):
    """
    Client to interact with Experiments api
    """
    def __init__(self):
        self.url = "/experiment/{id}"
        super(ExperimentClient, self).__init__()

    def get_all(self):
        experiment_config = ExperimentConfigManager.get_config()
        experiments_dict = self.request("GET",
                                self.url,
                                params="family_id={}".format(experiment_config.family_id))
        return [Experiment.from_dict(expt) for expt in experiments_dict]

    def get(self, id):
        experiment_dict = self.request("GET",
                                       url=self.url.format(id=id))
        return Experiment.from_dict(experiment_dict)


    def stop(self, id):
        self.request("POST",
                     url=self.url.format(id=id),
                     params={'action': 'stop'})
        return True

    def create(self, experiment_request):
        response = self.request("POST",
                                url="/experiment/run",
                                data=json.dumps(experiment_request.to_dict()),
                                timeout=3600)
        return response.get("id")

    def delete(self, id):
        self.request("DELETE",
                     "/experiment/{}".format(id))
        return True

    def get_log_server(self, id):
        log_dict = self.request("GET",
                                "/task/{}/log".format(id))
        if log_dict.get('method') == 'kafka':
            return log_dict.get('server')
        return None

    def get_task_detail(self, id):
        url = "/task/%s" % id
        response = self.request("GET",
                                url=url,
                                params={"content": "detail"})
        return response

    def get_task_url(self, id):
        res = self.get_task_detail(id)
        if isinstance(res, dict):
            return dict(jupyter_url=res.get('jupyter_url'),
                        tensorboard_url=res.get('tensorboard_url'))
        else:
            return dict()