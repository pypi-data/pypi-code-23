import io
import json
import sys

if sys.version_info >= (3, 0):
    from builtins import str
    unicode = str


class UploadReportsRequest(object):
    def __init__(self, agent_data, report_file):
        self.agentData = io.StringIO(unicode(json.dumps(agent_data, default=lambda m: m.__dict__)))
        self.report = report_file
