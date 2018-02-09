import pyoozie
from pyoozie import xml
from pyoozie import exceptions
from pyoozie import tags

def _bundle_submission_xml(username, coord_xml_path, configuration=None, indent=False):
    """Generate a Coordinator XML submission message to POST to Oozie."""
    submission = tags.Configuration(configuration)
    submission.update({
        'user.name': username,
        'oozie.bundle.application.path': coord_xml_path,
    })
    return submission.xml(indent)

class OozieClient:
    base_url = 'http://localhost:11000/oozie'
    user = 'hdfs'

    def __init__(self, base_url, user="hdfs"):
        self.base_url = base_url
        self.user = user

    def create_oozie_client(self):
        return pyoozie.OozieClient(url=self.base_url, user=self.user)

    def run_workflow(self, xml_path, configuration):
        c = self.create_oozie_client()
        job_id = c.jobs_submit_workflow(xml_path, configuration=configuration, start=True)
        return job_id

    def run_coordinator(self, xml_path, configuration):
        c = self.create_oozie_client()
        job_id = c.jobs_submit_coordinator(xml_path, configuration=configuration)
        return job_id

    def run_bundle(self, xml_path, configuration):
        c = self.create_oozie_client()

        user = self.user or 'oozie'
        conf = _bundle_submission_xml(user, xml_path, configuration=configuration)

        reply = c._post('jobs', conf)

        if reply and 'id' in reply:
            return reply['id']
        raise exceptions.OozieException.operation_failed('submit coordinator')