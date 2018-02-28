import logging

from python_agent.common.build_session.build_session_data import BuildSessionData
from python_agent.common.constants import BUILD_SESSION_ID_FILE
from python_agent.common.http.backend_proxy import BackendProxy


log = logging.getLogger(__name__)


class Config(object):

    def __init__(self, config_data, app_name, branch_name, build_name, build_session_id, workspacepath, include, exclude):
        self.config_data = config_data
        self.app_name = app_name
        self.branch_name = branch_name
        self.build_name = build_name
        self.build_session_id = build_session_id
        self.backend_proxy = BackendProxy(config_data)
        self.build_session_id_filename = BUILD_SESSION_ID_FILE
        self.workspacepath = workspacepath
        self.include = include
        self.exclude = exclude

    def execute(self):
        additional_params = {
            "workspacepath": self.workspacepath,
            "include": self.include,
            "exclude": self.exclude
        }
        build_session_data = BuildSessionData(self.app_name, self.build_name, self.branch_name, self.build_session_id,
                                              additional_params=additional_params)
        build_session_id = self.backend_proxy.create_build_session_id(build_session_data)
        log.info("Received Build Session Id: %s" % build_session_id)
        try:
            with open(self.build_session_id_filename, "w") as f:
                build_session_id = build_session_id.replace("\"", "")
                f.write(build_session_id)
        except Exception as e:
            log.error("Failed Saving Build Session Id File to: %s. Error: %s" % (self.build_session_id_filename, str(e)))

