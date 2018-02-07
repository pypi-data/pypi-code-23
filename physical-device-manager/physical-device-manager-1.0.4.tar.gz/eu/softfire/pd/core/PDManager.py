import json

import yaml
from sdk.softfire.grpc import messages_pb2
from sdk.softfire.manager import AbstractManager
from sdk.softfire.utils import TESTBED_MAPPING
import urllib.parse
import requests

from eu.softfire.pd.utils.utils import get_available_physical_resources, get_logger

logger = get_logger(__name__)


class PhysicalResourceException(Exception):
    def __init__(self, message):
        self.message = message


class PDManager(AbstractManager):
    def refresh_resources(self, user_info) -> list:
        """
        List resources of physical-device-manager
        :param user_info:
        :return:
        """
        return super().refresh_resources(user_info)

    def validate_resources(self, user_info=None, payload=None) -> None:
        """
        Check syntax of requested resources
        :param user_info:
        :param payload: yaml
        :return:
        """
        request_dict = yaml.load(payload)
        logger.info("Validating: %s " % request_dict)

        resource_id = request_dict.get("properties").get('resource_id')
        if resource_id not in get_available_physical_resources().keys():
            raise PhysicalResourceException(
                "Resource id '%s' not in the valid options: %s" % (
                    resource_id, get_available_physical_resources().keys()))
        try:
            resource_name = request_dict.get("properties").get('resource_name')
        except ValueError as e:
            raise PhysicalResourceException(
                "Resource name not specified."
            )

        if resource_id == 'surrey-ue':
            # Check reachability of UE reservation engine
            resource_data = None
            testbed = None
            for k, v in self._resource_data.items():
                if v.get('resource_id') == resource_id:
                    logger.debug("resource '%s' found!" % resource_id)
                    resource_data = v
                    testbed = k
                    break

            if testbed is None or resource_id is None:
                raise PhysicalResourceException("Invalid resource %s" % resource_id)

            targeturl = urllib.parse.urljoin(resource_data.get("url"), "test")
            logger.info("Connecting to UE reservation engine: %s" % targeturl)
            r = requests.get(targeturl)
            logger.debug("response from UE reservation engine: %s" % r)

            if r.status_code == 500:
                raise PhysicalResourceException("Cannot reach UE reservation engine. Message: %s" % r.content)

            status = 'down'
            try:
                response = r.json()
                status = response.get("status")
            except ValueError as e:
                logger.error("Error connecting to UE reservation engine: %s" % e)
                raise PhysicalResourceException("Cannot reach UE reservation engine.")

            if status == 'up':
                pass

        else:
            pass

    def release_resources(self, user_info, payload=None) -> None:
        """
        Release physical resource reservation
        :param user_info:
        :param payload: 
        :return:
        """
        try:
            user_name = user_info.name
            logger.info("Terminating UE reservation(s) of user: %s" % user_name)
            try:
                res_dict = json.loads(payload)
            except ValueError as e:
                logger.error("Error parsing json resources: %s" % e)
                return

            if res_dict:
                resource_id = res_dict.get("properties").get("resource_id")
                resource_name = res_dict.get("properties").get("resource_name")
                logger.debug("resource id: %s" % resource_id)
                resource_data = None
                testbed = None
                for k, v in self._resource_data.items():
                    if v.get('resource_id') == resource_id:
                        resource_data = v
                        testbed = k
                if testbed is None or resource_id is None or resource_name is None:
                    logger.warn("Resource not found, probaly never deployed. I will return.")
                    return
                targeturl = urllib.parse.urljoin(resource_data.get("url"), "ue/terminate")
                logger.info("Connecting to UE reservation engine: %s" % targeturl)
                r = requests.delete(targeturl, headers={"Authorization": "Bearer " + resource_data.get("secret"),
                                                        "Content-Type": "application/json"},
                                    json={"username": user_name, "resourceId": resource_name})
                logger.debug("response from UE reservation engine: %s" % r)

            if r.status_code == 500:
                raise PhysicalResourceException("UE release failed. Message: %s" % r.content)

        except:
            logger.error("Error while releasing resource: %s. ignoring..." % payload)

    def create_user(self, user_info):
        pass

    def list_resources(self, user_info=None, payload=None) -> list:
        """
        Release physical resource reservation
        :param user_info:
        :param payload: 
        :return:
        """
        user_name = user_info.name
        logger.info("Call to list available physical resources from user: %s" % user_name)
        result = []
        self._resource_data = dict()

        for k, v in get_available_physical_resources().items():
            testbed = v.get('testbed')
            node_type = v.get('node_type')
            cardinality = int(v.get('cardinality'))
            description = v.get('description')
            resource_id = k
            testbed_id = TESTBED_MAPPING.get(testbed)
            logger.debug("resource_id: %s, testbed_id: %s" % (resource_id, testbed_id))
            if testbed_id is not None:
                result.append(messages_pb2.ResourceMetadata(resource_id=resource_id,
                                                            description=description,
                                                            cardinality=cardinality,
                                                            node_type=node_type,
                                                            testbed=testbed_id))
                if k == 'surrey-ue':
                    private = v.get('private')
                    self._resource_data[testbed] = dict(url=private.get('url'), secret=private.get('secret'),
                                                        resource_id=resource_id, testbed=testbed)

        logger.info("Returning %d resources" % len(result))
        return result

    def provide_resources(self, user_info, payload=None) -> list:
        """
        Reserve UEs at UE reservation engine
        :param user_info:
        :param payload: json
        :return:
        """
        result = list()
        user_name = user_info.name
        res_dict = json.loads(payload)
        resource_id = res_dict.get("properties").get("resource_id")
        resource_name = res_dict.get("properties").get("resource_name")
        logger.info("Call to reserve UE for user %s" % user_name)
        resource_data = None
        testbed = None
        for k, v in self._resource_data.items():
            if v.get('resource_id') == resource_id:
                logger.debug("resource '%s' found!" % resource_id)
                resource_data = v
                testbed = k
                break

        if testbed is None or resource_id is None:
            raise PhysicalResourceException("Invalid resource %s" % resource_id)

        targeturl = urllib.parse.urljoin(resource_data.get("url"), "ue/reserve")
        logger.info("Connecting to UE reservation engine: %s" % targeturl)
        r = requests.post(targeturl, json={"username": user_name, "resourceId": resource_name},
                          headers={"Authorization": "Bearer " + resource_data.get("secret"),
                                   "Content-Type": "application/json"})
        logger.debug("response from UE reservation engine: %s" % r)

        if r.status_code == 500:
            raise PhysicalResourceException("UE reservation failed. Message: %s" % r.content)

        try:
            response = r.json()
            url = response.get("url")
            email = response.get("email")
            password = response.get("password")
            ue_name = response.get("ue_name")
        except ValueError as e:
            logger.error("Error reading response json from UE reservation engine: %s" % e)
            raise PhysicalResourceException("Cannot reserve UE resource")

        result.append(json.dumps(
            {
                "type": "PhysicalResource",
                "properties": {
                    "resource_id": resource_id,
                    "resource_name": resource_name,
                    "URL": url,
                    "login": email,
                    "password": password,
                    "ue_name": ue_name
                }
            }
        ))

        return result
