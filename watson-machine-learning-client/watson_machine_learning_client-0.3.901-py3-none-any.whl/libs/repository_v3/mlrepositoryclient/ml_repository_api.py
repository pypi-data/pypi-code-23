################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################


from repository_v3.swagger_client.apis.repository_api import RepositoryApi
from repository_v3.swagger_client.rest import ApiException

import requests, certifi

try:
    import urllib3
except ImportError:
    raise ImportError('urllib3 is missing')

try:
    # for python3
    from urllib.parse import urlencode
except ImportError:
    # for python2
    from urllib import urlencode

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where()
)


class MLRepositoryApi(RepositoryApi):
    """
    MLRepositoryApi extends RepositoryApi.
    """
    def __init__(self, api_client):
        super(MLRepositoryApi, self).__init__(api_client)

    def upload_pipeline_version(self, pipeline_id, version_id, content_stream):
        r = requests.put('{}/v3/ml_assets/training_definitions/{}/versions/{}/content'.format(
            self.api_client.repository_path,
            pipeline_id,
            version_id
        ),
            headers=self.api_client.default_headers,
            data=content_stream
        )

        if r.status_code != 200:
            raise ApiException(r.status_code, r.text)

    def upload_pipeline_model_version(self, model_id, version_id, content_stream):
        r = requests.put('{}/v3/ml_assets/models/{}/versions/{}/content'.format(
            self.api_client.repository_path,
            model_id,
            version_id
        ),
            headers=self.api_client.default_headers,
            data=content_stream
        )

        if r.status_code != 200:
            raise ApiException(r.status_code, r.text)

    def download_artifact_content(self, artifact_content_href, accept='application/octet-stream'):
        #if artifact_content_href.startswith(self.api_client.repository_path):
        query_params = {}
        header_params = {'Accept': accept}

        try:
            return self.api_client.download_file(
                   artifact_content_href,
                   query_params,
                   header_params
               )

        except ApiException as ex:
                raise ex
        #else:
        #    raise ValueError('The artifact content href: {} is not within the client host: {}'
        #                     .format(artifact_content_href,
        #                             self.api_client.repository_path))
