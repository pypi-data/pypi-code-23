import itculate_sdk as itsdk

# server_url = "http://localhost:5000/api/v1"
from unix_dates import UnixDate, UnixTimeDelta

api_key = "fwvU0f5H1eLmcKyqcauXE4nEDhPZQzWT"
api_secret = "KgelEfRDLTESk2olOnH2CJq_g2zEYrIBlYTuNzktd6HjmzCFu7_79ygQdgjh-h1D"

account = "716756199562"
regions = ["us-east-1", "eu-central-1", "ap-northeast-1"]
collector_id = "collector_id"


class Rapid7Client(object):
    def __init__(self):
        itsdk.init(api_key=api_key, api_secret=api_secret)
        itsdk.vertex_event(collector_id="event",
                           vertex="716756199562:us-east-1|product:platform|service:platform-collector-app",
                           message="Property tags.Version changed from 1.12.9 to 1.12.10",
                           event_type="Property Changed",
                           timestamp=UnixDate.now() - UnixTimeDelta.calc(hours=(24 * 4 + 2)))
        itsdk.flush_all()

#
#     @classmethod
#     def _service_key(cls, region, product, service):
#         return "{}:{}|product:{}|service:{}".format(account, region, product, service)
#
#     def create_data_processing_pipeline(self):
#         # get the service to connect
#
#         for r in regions:
#             doc_normalizer_key = self._service_key(region=r, product="insightidr", service="doc-normalizer")
#             attribution_key = self._service_key(region=r, product="insightidr", service="attribution")
#             behavior_generation_key = self._service_key(region=r, product="insightidr", service="behavior-generation")
#             incident_generation_key = self._service_key(region=r, product="insightidr", service="incident-generation")
#
#             itsdk.connect(collector_id=collector_id,
#                           source=doc_normalizer_key,
#                           target=attribution_key,
#                           topology="uses-attribution")
#             itsdk.connect(collector_id=collector_id,
#                           source=attribution_key,
#                           target=behavior_generation_key,
#                           topology="uses-behavior_generation")
#             itsdk.connect(collector_id=collector_id,
#                           source=behavior_generation_key,
#                           target=incident_generation_key,
#                           topology="uses-incident_generation")
#
#     def connect_collector_services(self):
#         for r in regions:
#             collector_app_key = self._service_key(region=r, product="platform", service="platform-collector-app")
#             collector_boss_key = self._service_key(region=r, product="insightidr", service="collector-boss")
#             endpoint_app_key = self._service_key(region=r, product="insightidr", service="endpoint-ingress-app")
#
#             itsdk.connect(collector_id=collector_id,
#                           source=collector_boss_key,
#                           target=collector_app_key,
#                           topology="uses-platform@platform-collector-app")
#             itsdk.connect(collector_id=collector_id,
#                           source=collector_boss_key,
#                           target=endpoint_app_key,
#                           topology="uses-insightidr@endpoint-ingress-app")
#
#             # Create collector ElasticSearch Service and connect the ASG to it
#             elasticsearch_service = "collector-elasticsearch/{}".format(r)
#             itsdk.add_vertex(collector_id=collector_id,
#                              vertex_type="Service",
#                              name=elasticsearch_service,
#                              keys=elasticsearch_service,
#                              region=r)
#
#             # Connect the ElasticSearch ASG to the Service and the Service the collector_app_key service
#             if r == "us-east-1":
#                 es_asg_key = "escqplatformcollector-razor-d0prod-r01-v002"
#             elif r == "eu-central-1":
#                 es_asg_key = "escqplatformcollector-razor-d0prod-r00-v005"
#             elif r == "ap-northeast-1":
#                 es_asg_key = "escqplatformcollector-razor-d0prod-r02"
#             else:
#                 assert False, "Unsupported region {}".format(r)
#
#             itsdk.connect(collector_id=collector_id,
#                           source=elasticsearch_service,
#                           target=es_asg_key,
#                           topology="auto_scaling_group")
#
#             itsdk.connect(collector_id=collector_id,
#                           source=collector_app_key,
#                           target=elasticsearch_service,
#                           topology="uses-elasticsearch")
#
#     def connect_rds_customer_master(self):
#
#         region = "us-east-1"
#
#         attribution_key = self._service_key(region=region, product="insightidr", service="attribution")
#         behavior_generation_key = self._service_key(region=region, product="insightidr", service="behavior-generation")
#         incident_generation_key = self._service_key(region=region, product="insightidr", service="incident-generation")
#         rds_key = "arn:aws:rds:{}:716756199562:db:customer-master-razor-prod-1".format(region)
#
#         topology = "uses-rds-customer-master"
#         itsdk.connect(source=attribution_key, target=rds_key, topology=topology, collector_id=collector_id)
#         itsdk.connect(source=behavior_generation_key, target=rds_key, topology=topology, collector_id=collector_id)
#         itsdk.connect(source=incident_generation_key, target=rds_key, topology=topology, collector_id=collector_id)
#
#     def connect_consumers(self, region, target, topology, product, consumers):
#         for consumer in consumers:
#             service_key = self._service_key(region=region, product=product, service=consumer)
#             print(service_key)
#             itsdk.connect(source=service_key,
#                           target=target, topology=topology, collector_id=collector_id)
#
#     def connect_shared_redis(self):
#         self.connect_consumers(region="us-east-1",
#                                target="elasticache.redis.ec1875edc13ff0069446",
#                                topology="uses-redis-razor-cache-dynamic",
#                                product="insightidr",
#                                consumers=["attribution",
#                                           "behavior-generation",
#                                           "doc-normalizer",
#                                           "monolith-bridge-app",
#                                           "virus-total-integration"])
#
#     def bla(self):
#         services = [
#             ("insightidr", "razor-ui"),
#             ("insightidr", "collector-boss"),
#             ("insightidr", "attribution"),
#             ("insightidr", "incident-generation"),
#             ("insightidr", "razor-job"),
#             ("platform", "endpoint-boss-app"),
#             ("platform", "logentries-link-app"),
#             ("insightidr", "doc-normalizer"),
#             ("insightidr", "monolith-bridge-app"),
#             ("insightidr", "platform-ui"),
#             ("insightidr", "behavior-generation"),
#             ("insightidr", "blob-processor"),
#         ]
#
#         collector_app_service_key = self._service_key(region="us-east-1",
#                                                       product="platform",
#                                                       service="platform-collector-app")
#         for product, service in services:
#             service_key = self._service_key(region="us-east-1", product=product, service=service)
#             itsdk.connect(source=collector_app_service_key,
#                           target=service_key,
#                           topology="WTF",
#                           collector_id=collector_id)
#
#             # "escqplatformcollector/us-east-1"
#
#
if __name__ == '__main__':
    client = Rapid7Client()
#     client.create_data_processing_pipeline()
#     client.connect_collector_services()
#     client.connect_rds_customer_master()
#     client.connect_shared_redis()
#     client.bla()
#     itsdk.flush_all()

#
# INSERT INTO imodel.vertex_events (tenant, vertex_rid, event_time, rid, event_type, message, severity)
# VALUES ('3nvQ3n6nk1j1X6nji34PB',
#         '3nvQ3n6nk1j1X6nji34PB_SERVICE_DISCOVERY_51744622676_235',
#         1510794486.7331988811,
#         '7e578b55-7c03-3561-8bec-99135648xxx',
#         'Property Changed', 'Property tags.Version changed from 1.12.9 to 1.12.10', 'INFO')