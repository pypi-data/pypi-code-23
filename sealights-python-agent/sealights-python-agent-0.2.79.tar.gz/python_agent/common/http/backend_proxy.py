import json
import logging

from python_agent.common.build_session.build_session_data import BuildSessionData
from python_agent.common.http.requests_wrapper import Requests
from python_agent.common.http.sl_routes import SLRoutes
from python_agent.packages import requests
from python_agent import __package_name__ as PACKAGE_NAME
from python_agent import __version__ as VERSION
from python_agent.packages.requests import HTTPError

log = logging.getLogger(__name__)


class BackendProxy(object):

    def __init__(self, config_data):
        self.requests = Requests(config_data)
        self.config_data = config_data

    def get_build_session(self, build_session_id):
        try:
            response = self.requests.get(SLRoutes.build_session_v2(build_session_id))
            response.raise_for_status()
            response = response.json()
            build_session_data = BuildSessionData(response["appName"], response["buildName"], response["branchName"],
                                                  response["buildSessionId"], additional_params=response.get("additionalParams"))
            return build_session_data
        except HTTPError as e:
            if (e.response.status_code == 404):
                log.error("Server returned 404 (Not Found) for build session id %s. " % build_session_id)
            else:
                log.exception("Failed getting Build Session Id. Error: %s" % str(e))
        except Exception as e:
            log.exception("Failed getting Build Session Id. Error: %s" % str(e))

        return None

    def create_build_session_id(self, build_session_data):
        try:
            response = self.requests.post(SLRoutes.build_session_v2(), data=json.dumps(build_session_data, default=lambda m: m.__dict__))
            response.raise_for_status()
            build_session_id = response.content
            return build_session_id
        except Exception as e:
            log.exception("Failed Creating Build Session Id. Error: %s" % str(e))
            return None

    def submit_build_mapping(self, build_mapping):
        response = self.requests.post(SLRoutes.build_mapping_v3(), data=json.dumps(build_mapping, default=lambda m: m.__dict__))
        response.raise_for_status()

    def send_footprints(self, footprints):
        response = self.requests.post(SLRoutes.footprints_v5(), data=json.dumps(footprints, default=lambda m: m.__dict__))
        response.raise_for_status()

    def send_events(self, events):
        response = self.requests.post(SLRoutes.events_v2(), data=json.dumps(events, default=lambda m: m.__dict__))
        response.raise_for_status()

    def start_execution(self, start_execution_request):
        response = self.requests.post(SLRoutes.test_execution_v3(), data=json.dumps(start_execution_request, default=lambda m: m.__dict__))
        response.raise_for_status()

    def end_execution(self, labid):
        response = self.requests.delete(SLRoutes.test_execution_v3(), params={"environment": labid})
        response.raise_for_status()

    def upload_reports(self, upload_reports_request):
        response = self.requests.post(SLRoutes.external_data_v3(), files=upload_reports_request.__dict__, patch_content_type=False)
        response.raise_for_status()

    def has_active_execution(self, customer_id, labid):
        params = {
            "customerId": customer_id,
            "labId": labid,
            "environment": labid
        }
        try:
            log.info("[TO TST] - send TestExecutionRequest. Request url: %s. params: %s" % (SLRoutes.test_execution_v3(), params))
            response = self.requests.get(SLRoutes.test_execution_v3(), params=params)
            parsed_response = {}
            if response.content:
                parsed_response = response.json()
            log.info("[FROM TST] - received TestExecutionResponse. Response: %s" % parsed_response)

            status = parsed_response.get("status")
            if status in ["pendingDelete", "created"]:
                return True
            if response.status_code == requests.codes.not_found:
                log.info("[FROM TST] - Couldn't find any mapping for the specified parameters.")
                return False
        except Exception as e:
            log.exception("[FROM TST] - Error while trying to send request. Error: %s" % str(e))
            return False

    def submit_logs(self, logs_request):
        response = self.requests.post(SLRoutes.logsubmission_v2(), data=json.dumps(logs_request, default=lambda m: m.__dict__))
        response.raise_for_status()

    def get_recommended_version(self):
        try:
            response = self.requests.get(SLRoutes.recommended_v2())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.warning("Failed Getting Recommended Version. Error: %s" % str(e))
            return {}

    def check_version_exists_in_pypi(self, version):
        url = "https://pypi.python.org/pypi/%s/%s" % (PACKAGE_NAME, version)
        try:
            response = self.requests.get(url)
            response.raise_for_status()
            return True
        except Exception as e:
            log.warning("Version: %s Doesn't exist. URL: %s. Error: %s" % (version, url, str(e)))
            return False

    def get_remote_configuration(self):
        try:
            url = SLRoutes.configuration_v2(self.config_data.customerId, self.config_data.appName, self.config_data.branchName, self.config_data.testStage, PACKAGE_NAME, VERSION)
            response = self.requests.get(url)
            response.raise_for_status()
            response = response.json()
            config_as_json = response["config"]
            if ((config_as_json != None) and (config_as_json != "")):
                log.info("Server returned The following configuration: '%s'" % config_as_json)
                config = json.loads(config_as_json)
                return config
        except HTTPError as e:
            if (e.response.status_code == 404):
                log.info("Server returned 404 (Not Found) for remote configuration. Using loaded configuration. ")
            else:
                log.warning("Failed getting remote configuration. Error: %s" % str(e))
        except Exception as e:
            log.warning("Failed getting remote configuration. Error: %s" % str(e))

        return {}

