import hashlib
import json
import urllib
from datetime import datetime
from urllib import parse

import requests
import yaml
from sdk.softfire.grpc import messages_pb2
from sdk.softfire.grpc.messages_pb2 import UserInfo
from sdk.softfire.main import start_manager
from sdk.softfire.manager import AbstractManager
from sdk.softfire.utils import TESTBED_MAPPING

from eu.softfire.sdn.utils.exceptions import SdnManagerException
from eu.softfire.sdn.utils.static_config import CONFIG_FILE_PATH
from eu.softfire.sdn.utils.utils import get_logger, get_available_resources

logger = get_logger(__name__)

testbed2str = {
    messages_pb2.FOKUS: "fokus",
    messages_pb2.FOKUS_DEV: "fokus-dev",
    messages_pb2.ERICSSON: "ericsson",
    messages_pb2.SURREY: "surrey",
    messages_pb2.ADS: "ads",
    messages_pb2.DT: "dt",
}


class SdnManager(AbstractManager):
    def __init__(self, config_file_path):
        super().__init__(config_file_path)
        self._resource_data = dict()
        logger.info("calling list_resources to load resource details...")
        self.list_resources()

    def remove_tenant(self, tenant_id, testbed_str):
        ##remove tenant from proxy
        testbed = TESTBED_MAPPING.get(testbed_str)
        logger.debug(
            "remove_tenant: checking if tenant %s is already prepared on testbed %s" % (tenant_id, testbed_str))
        # TODO: send tenand_id to proxy
        if testbed is messages_pb2.FOKUS_DEV:  ## opensdncore openstack
            res = [x for x in self._resource_data.values() if x.get("testbed") == testbed_str][0]

            url = urllib.parse.urljoin(res.get("url"), "RemoveTenant/%s" % tenant_id)
            #data = dict(tenant_id=tenant_id)
            logger.info("calling /RemoveTenant on SDN-Proxy-FOKUS...")
            r = requests.delete(url, headers={"Auth-Secret": res["secret"]})
            if r.status_code == 200:
                logger.info("Tenant Deletion successful %s" % r)
            else:
                logger.error("Problem in Tenant Deletion")

        elif testbed is messages_pb2.FOKUS:  # normal openstack

            logger.info("no SDN support on %s" % testbed)
            pass
        elif testbed is messages_pb2.ERICSSON:
            logger.info("no SDN support on %s" % testbed)
            pass
        elif testbed is messages_pb2.ERICSSON_DEV:
            logger.info("no SDN support on %s" % testbed)
            pass
        else:
            logger.error("testbed %s unknown!" % testbed)

    def prepare_tenant(self, tenant_id, testbed_str):
        testbed = TESTBED_MAPPING.get(testbed_str)
        logger.debug(
            "prepare_tenant: checking if tenant %s is already prepared on testbed %s" % (tenant_id, testbed_str))
        # TODO: send tenand_id to proxy
        if testbed is messages_pb2.FOKUS_DEV:  ## opensdncore openstack
            res = [x for x in self._resource_data.values() if x.get("testbed") == testbed_str][0]

            url = urllib.parse.urljoin(res.get("url"), "PrepareTenant")
            data = dict(tenant_id=tenant_id)
            logger.info("calling /PrepareTenant on SDN-Proxy-FOKUS...")
            r = requests.post(url, json=data, headers={"Auth-Secret": res["secret"]})
            if r.headers.get('Content-Type', "") == "application/json" and r.status_code == 200:
                try:
                    resj = r.json()
                    logger.debug("Result from SDN-Proxy: %s" % resj)
                    return resj.get("flow-table-offset")
                except ValueError as e:
                    logger.error("Error reading response json: %s" % e)
                    raise SdnManagerException("error during PrepareTenant")
            pass
        elif testbed is messages_pb2.FOKUS:  # normal openstack

            logger.info("no SDN support on %s" % testbed)
            pass
        elif testbed is messages_pb2.ERICSSON:
            logger.info("no SDN support on %s" % testbed)
            pass
        elif testbed is messages_pb2.ERICSSON_DEV:
            logger.info("no SDN support on %s" % testbed)
            pass
        else:
            logger.error("testbed %s unknown!" % testbed)

    # def setup_sdn_proxy(self, token, tenant, resource_id):
    #     res = self._resource_data[resource_id]
    #     url = urllib.parse.urljoin(res.get("url"), "SDNproxySetup")
    #     data = dict(experiment_id=token, tenant_id=tenant)
    #     r = requests.post(url, json=data, headers=["Auth-Secret: " + res["secret"]])
    #     if r.headers.get('Content-Type') and r.headers['Content-Type'] == "application/json":
    #         try:
    #             resj = r.json()
    #             logger.debug("Result from SDN-Proxy: %s" % resj)
    #             return resj.get("user-flow-tables")
    #         except ValueError as e:
    #             logger.error("Error reading response json: %s" % e)
    #             raise SdnManagerException("Can't setup SDN-Proxy")

    def release_resources(self, user_info, payload=None) -> None:
        """
        extract token from payload and delete token at the proxy
        :param user_info:
        :param payload: JSON object { "resource_id", "flow-table-range", "token", "URI", }
        :return:
        """
        try:
            pj = json.loads(payload)
        except ValueError as e:
            logger.error("error parsing json resources: %s" % e)
            return

        self._terminate_resource(pj)

    def _terminate_resource(self, pj):
        logger.debug("Terminating resource: %s" % pj)
        if pj:
            res_id = pj.get("resource_id")
            token = pj.get("token")
            resource_data = None
            testbed = None
            for k, v in self._resource_data.items():
                if v.get('resource_id') == res_id:
                    resource_data = v
                    testbed = k
            if testbed is None or res_id is None:
                logger.warn("Resource not found! probaly never deployed, i will return")
                return
            targeturl = urllib.parse.urljoin(resource_data.get("url"), "SDNproxy/%s" % token)
            logger.info("Deleting sdn-proxy: %s" % targeturl)
            r = requests.delete(targeturl, headers={"Auth-Secret": resource_data.get("secret")})
            logger.debug("Result: %s" % r)

    def list_resources(self, user_info=None, payload=None) -> list:
        logger.info("Received List Resources")
        logger.debug("UserInfo: %s" % user_info)
        result = []

        self._resource_data = dict()

        for k, v in get_available_resources().items():
            testbed = v.get('testbed')
            node_type = v.get('node_type')
            cardinality = int(v.get('cardinality'))
            description = v.get('description')
            resource_id = k
            testbed_id = TESTBED_MAPPING.get(testbed)
            logger.debug("res %s Testbed ID: %s" % (resource_id, testbed_id))
            if testbed_id is not None:
                result.append(messages_pb2.ResourceMetadata(resource_id=resource_id,
                                                            description=description,
                                                            cardinality=cardinality,
                                                            node_type=node_type,
                                                            testbed=testbed_id))
                private = v.get('private')
                self._resource_data[testbed] = dict(url=private.get('url'), secret=private.get('secret'),
                                                    resource_id=resource_id, testbed=testbed)

        logger.info("returning %d resources" % len(result))
        return result

    def validate_resources(self, user_info=None, payload=None) -> None:
        """
        Check syntax of requested resources
        :param user_info:
        :param payload: yaml
        :return:
        """
        logger.debug("validate_resources payload: %s" % payload)
        res_dict = yaml.load(payload)
        logger.debug("validate_resources dict: %s" % res_dict)
        resource_id = res_dict.get("properties").get("resource_id")
        logger.debug("Validate resource: %s" % resource_id)
        if resource_id not in [v.get('resource_id') for k, v in self._resource_data.items()]:
            raise KeyError("Unknown resource_id")

    def provide_resources(self, user_info: UserInfo, payload=None) -> list:
        """
        Call /SetupProxy API on sdn-proxy
        :param user_info:
        :param payload: json
        :return:
        """
        result = list()
        res_dict = json.loads(payload)
        logger.debug("provide_resources dict %s" % res_dict)
        logger.debug("provide_resources user_info %s %s" % (type(user_info), user_info))
        resource_id = res_dict.get("properties").get("resource_id")
        logger.debug("provide_resources: res_dict: %s" % res_dict)
        logger.info("provide_resources username:%s resource:%s " % (user_info.name, res_dict))
        resource_data = None
        testbed = None
        for k, v in self._resource_data.items():
            logger.debug("provide_resources: list _resourcedata: %s: %s" % (k, v))
            if v.get('resource_id') == resource_id:
                logger.debug("found resource!(testbed=%s)" % k)
                resource_data = v
                testbed = k
                break

        if testbed is None or resource_id is None:
            raise SdnManagerException("Invalid resources!")

        user_name = user_info.name
        token_string = "%s%s%s" % (resource_id, datetime.utcnow(), user_name)
        token = hashlib.md5(token_string.encode()).hexdigest()
        tenant_id = user_info.testbed_tenants[TESTBED_MAPPING.get(testbed)]
        logger.debug("genrated_token: %s" % token)
        data = dict(experiment_id=token, tenant_id=tenant_id)

        targeturl = urllib.parse.urljoin(resource_data.get("url"), "SDNproxySetup")
        logger.debug("Target SDN-Proxy URL: %s" % targeturl)
        r = requests.post(targeturl, json=data, headers={"Auth-Secret": resource_data.get("secret")})
        logger.debug("Result: %s" % r)

        if r.status_code == 500:
            raise SdnManagerException("SDNproxySetup failed. Message: %s" % r.content)

        if r.headers.get('Content-Type') and r.headers['Content-Type'] == "application/json":
            try:
                resj = r.json()
                logger.debug("Result from SDN-Proxy: %s" % resj)
                user_flow_tables = resj.get("user-flow-tables", None)
                api_url = resj.get("endpoint_url")
            except ValueError as e:
                logger.error("Error reading response json: %s" % e)
                raise SdnManagerException("Can't setup SDN-Proxy")

            result.append(json.dumps(
                {
                    "resource_id": resource_id,
                    "flow-table-range": user_flow_tables,
                    "token": token,
                    "URI": api_url
                }
            ))

        return result

    def delete_user(self, user_info: UserInfo):
        logger.debug("delete_user UserInfo: %s" % user_info)
        logger.debug("delete_user testbed_tenants: %s" % user_info.testbed_tenants)
        # call remove_tenant
        for testbed_id, tenent_id in user_info.testbed_tenants.items():
            if tenent_id and testbed_id in testbed2str.keys():
                if testbed_id == messages_pb2.FOKUS_DEV:
                    self.remove_tenant(tenent_id, testbed2str.get(testbed_id))
            else:
                logger.error("delete_user: Tenant_id missing for testbed %s!" % testbed2str.get(testbed_id))
        return user_info

    def create_user(self, user_info: UserInfo) -> UserInfo:
        logger.debug("create_user UserInfo: %s" % user_info)
        logger.debug("create_user testbed_tenants: %s" % user_info.testbed_tenants)
        for testbed_id, tenent_id in user_info.testbed_tenants.items():
            if tenent_id and testbed_id in testbed2str.keys():
                if testbed_id == messages_pb2.FOKUS_DEV:
                    self.prepare_tenant(tenent_id, testbed2str.get(testbed_id))
            else:
                logger.error("create_user: Tenant_id missing for testbed %s!" % testbed2str.get(testbed_id))
        return user_info

    def refresh_resources(self, user_info) -> list:
        """
        used for refreshing the image list for nvf-maanger(s)
        :param user_info:
        :return:
        """
        return super().refresh_resources(user_info)


def start():
    start_manager(SdnManager(CONFIG_FILE_PATH))


if __name__ == '__main__':
    print("##### SoftFIRE - SDN-Manager #####")
    start()
