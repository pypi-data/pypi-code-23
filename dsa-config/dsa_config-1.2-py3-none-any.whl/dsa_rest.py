"""
Common class to support DSC REST APIs.

Current REST APIs support:
1.  Get available media servers in DSC
2. Configure AWS.
3. Create S3 target group.
4. Configure a Teradata database system.
5. Create media server
6. Enable Teradata database system.
7. Get the list of Teradata database systems registered with DSC.
"""
import requests
import json
import socket
import tdtestpy
import logging
import os
import sys
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(CURRENT_DIR, 'logs')

class DsaREST:
    DSC_PORT = "9090"
    AWS_BUCKET_NAME = 'awstqpesit'
    MEDIA_SERVER_PORT = 15406

    # DSC REST APIs
    get_registered_systems_url = "/dsa/components/systems/teradata"
    config_aws_url = "/dsa/components/aws-app"
    create_s3_target_group_url = "/dsa/components/target-groups/s3"
    config_system_url = "/dsa/components/systems/teradata"
    create_media_server_url = "/dsa/components/mediaservers"
    enable_system_url = "/dsa/components/systems/enabling/"
    get_media_servers_url = "/dsa/components/mediaservers"

    def __init__(
            self,
            dsc_server=None,
            dsc_password=None,
            media_server_name="test_media",
            target_media_name="test_target",
            prefix_name="dsa_storage/"):
        self._dsc_server = dsc_server
        self._dsc_password = dsc_password
        self._media_server_name = media_server_name
        self._target_media_name = target_media_name
        self._prefix_name = prefix_name
        self._http_prefix = 'http://{0}:{1}'.format(self._dsc_server, DsaREST.DSC_PORT)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        logname = "dsa_config_{}.log".format(timestamp)

        self.logger = tdtestpy.TdLogger(LOG_DIR, logname, standalone=True)
        self.logger.logger.addHandler(logging.StreamHandler(sys.stdout))

    @property
    def dsc_server(self):
        return self._dsc_server

    @dsc_server.setter
    def dsc_server(self, dsc_server):
        if dsc_server is None:
            raise ValueError("DSC server name / IP address invalid")
        self._dsc_server = dsc_server

    @property
    def dsc_password(self):
        return self._dsc_password

    @dsc_password.setter
    def dsc_password(self, dsc_password):
        if dsc_password is None:
            raise ValueError("DSC server password invalid")
        self._dsc_password = dsc_password

    def get_media_server_name(self):
        return self._media_server_name

    def get_target_media_name(self):
        return self._target_media_name

    def set_target_media_name(self, target_media_name):
        self._target_media_name = target_media_name

    def set_prefix_name(self, prefix_name):
        self._prefix_name = prefix_name

    def get_media_servers(self):
        """
        Get the media server list from DSC server
        :return: List of media servers configured with DSC
        """
        try:

            headers = self.get_header()
            url = self._http_prefix + DsaREST.get_media_servers_url

            response = requests.get(
                url,
                auth=('root', self._dsc_password),
                headers=headers)

            self.verify_http_response(response=response, request=url)
            if self.verify_http_response(response=response, request=url):
                return response.text
            else:
                return None
        except requests.HTTPError as e:
            raise e

    def get_dsc_media_server_name(self, media_servers):
        """
        Get the name of the media server that comes pre-configured with Teradata
        :param media_servers:
        :return: media server name
        """
        ip_address = self.get_ip(self._dsc_server)
        print("ip_address {0} of dsc_server {1}".format(ip_address, self._dsc_server))
        medias = json.loads(media_servers)["medias"]
        for media in medias:
            for ip_info in media["ips"]:
                if ip_address in ip_info["ipAddress"]:
                    return media["name"]

    @staticmethod
    def get_header():
        """
        HTTP request/response header.
        :return:
        HTTP header as dictionary
        """
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/vnd.com.teradata.rest-v1.0+json'
        headers['Accept-Encoding'] = None
        return headers

    @staticmethod
    def verify_http_response(response, request):
        """
        Verify http response
        :param response: http response
        :param request: Request url
        :return: True if the response is 200 else false
        """
        if response.status_code == 200:
            print("Request:  {0} \n Response text: {1} \n".format(request, response.json))
            return True
        else:
            print("Request: {0} \n Response code: {1} \n".format(request, response.json))
            return False

    def config_aws(self):
        """
        configure AWS S3 bucket with DSC server
        :return:
        status of AWS S3 configuration
        """

        s3 = tdtestpy.AWSS3(self.AWS_BUCKET_NAME)
        try:
            headers = self.get_header()
            access_id = s3.get_access_id()
            access_key = s3.get_access_key()

            with open('/root/payload_files/config_aws.json') as f:
                payload = json.load(f)
                payload["configAwsRest"]["acctName"] = self.AWS_BUCKET_NAME
                payload["configAwsRest"]["accessId"] = access_id
                payload["configAwsRest"]["accessKey"] = access_key
                payload["configAwsRest"]["bucketsByRegion"][0]["buckets"][0]["bucketName"] = self.AWS_BUCKET_NAME
                payload["configAwsRest"]["bucketsByRegion"][0]["buckets"][0]["prefixList"][0]["prefixName"] \
                    = self._prefix_name

            url = self._http_prefix + DsaREST.config_aws_url
            print("config aws url: {}".format(url))
            response = requests.post(
                url,
                auth=('root', self._dsc_password),
                headers=headers,
                json=payload)
            self.verify_http_response(response=response, request=url)
        except requests.HTTPError as e:
            raise e

    def create_s3_target_group(self, media_server_name):
        """
        Create target group for S3 storage.
        :param media_server_name: media server name used by the target group
        :return:
        Status of create target group request.
        """
        try:
            headers = self.get_header()
            with open('/root/payload_files/create_s3_target_group.json') as f:
                payload = json.load(f)
                payload["awsAccountName"] = self.AWS_BUCKET_NAME
                payload["targetGroupName"] = self._target_media_name
                payload["targetMediaBuckets"][0]["barMediaServer"] = media_server_name
                payload["targetMediaBuckets"][0]["buckets"][0]["bucketName"] = self.AWS_BUCKET_NAME
                payload["targetMediaBuckets"][0]["buckets"][0]["prefixList"][0]["prefixName"] = self._prefix_name

            url = self._http_prefix + DsaREST.create_s3_target_group_url
            response = requests.post(
                url,
                auth=('root', self._dsc_password),
                headers=headers,
                json=payload)
            self.verify_http_response(response=response, request=url)

        except requests.HTTPError as e:
            raise e


    def config_system(self, dbs_name, dbc_password):
        """
        Configure a teradata system with DSC server
        :param dbs_name: Teradata database name
        :param dbc_password: Teradata database password
        :return:
        Status of system configuration request
        """
        try:
            headers = self.get_header()
            with open('/root/payload_files/config_system.json') as f:
                payload = json.load(f)
                payload["systemName"] = dbs_name
                payload["tdpId"] = dbs_name
                payload["password"] = dbc_password

            url = self._http_prefix + DsaREST.config_system_url
            print("Config system URL {}".format(url))
            print("Config system headers {}".format(headers))
            print("Config system request body {}".format(payload))
            response = requests.post(
                url,
                auth=('root', self._dsc_password),
                headers=headers,
                json=payload)
            self.verify_http_response(response=response, request=url)

        except requests.HTTPError as e:
            raise e

    def create_media_server(self, ip_address):
        """
        create media server for the S3 in DSC server
        :param ip_address:
        :return:
        """

        try:
            headers = self.get_header()
            with open('/root/payload_files/create_media_server.json') as f:
                payload = json.load(f)
                payload["serverName"] = self._dsc_server
                payload["port"] = self.DSC_PORT
                payload["ipInfo"][0]["ipAddress"] = ip_address

            url = self._http_prefix + DsaREST.create_media_server_url

            response = requests.post(
                url,
                auth=('root', self._dsc_password),
                headers=headers,
                json=payload)
            self.verify_http_response(response=response, request=url)

        except requests.HTTPError as e:
            raise e

    def enable_system(self, system):
        """
        Enable a newly registered Teradata Database system
        :param system: Teradata Data
        :return:
        """
        try:
            headers = self.get_header()

            enable_system = system + '/'
            url = self._http_prefix + DsaREST.enable_system_url + enable_system

            response = requests.post(
                url,
                auth=('root', self._dsc_password),
                headers=headers)
            self.verify_http_response(response=response, request=url)

        except requests.HTTPError as e:
            raise e

    @staticmethod
    def get_ip(hostname):
        """
        Get IP address of any server
        :param hostname: server name
        :return:
        """
        ip_address = None
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.error as err:
            logging.error("Failed to fetch IP address of system: {0} with error: {1}".format(hostname, err))  # noqa: E501
            raise err

        return ip_address

    @staticmethod
    def registered_system_lookup(dbs, registered_systems):
        """
        Check if the database system is already registered with DSC server
        :param dbs: Teradata system(source/target)
        :param registered_systems: List of systems that are already registered with DSC server
        :return: True if the system is already registered with DSC
        """
        system_exists = False

        for system in registered_systems["systems"]:
            if system["systemName"] == dbs:
                system_exists = True
                print("SYSTEM EXISTS")
                break
        return system_exists

    def register_system(self, dbs, dbc_password, registered_systems):
        """
        Register a system with DSC server
        :param dbs: Teradata system
        :param dbc_password: Teradata database password
        :param registered_systems: list of systems registered with DSC
        :return:
        Boolean indicating the status of system registration
        """
        system_registered = False
        registered_systems = json.loads(registered_systems)
        print("Register system: {}".format(registered_systems))
        if registered_systems:
            if not self.registered_system_lookup(dbs, registered_systems):
                system_registered = True
                self.config_system(dbs, dbc_password)

        return system_registered

    def get_registered_systems(self):
        """
        Get the list of systems registered with DSC server
        :return:
        HTTP response for the register system request.
        """
        try:

            headers = self.get_header()
            url = self._http_prefix + DsaREST.get_registered_systems_url

            response = requests.get(
                url,
                auth=('root', self._dsc_password),
                headers=headers)
            if self.verify_http_response(response=response, request=url):
                return response.text
            else:
                return None

        except requests.HTTPError as e:
            raise e
