from collections import defaultdict
from examples.util import common_document
from itculate_sdk.connection import ApiConnection

import itculate_sdk as itsdk

# server_url = "http://localhost:5000/api/v1"
server_url = "https://api.itculate.io/api/v1"

tenant = "54JIuoGY8XRE7hRNgBzYYa"
api_key = "OHDZIClXaRZfOg51R3j40gKqhLQpwPQw"
api_secret = "gfFNhMX5PfxhdOeiID7ToHjKe4IjOnCraaAb-nDSU2m34EuEzhBTwSXDFxVE0yxJ"

itsdk.init(api_key=api_key, api_secret=api_secret, server_url=server_url)

connection = ApiConnection(api_key=api_key, api_secret=api_secret, server_url=server_url)
raw_vertices = connection.get("tenants/{}/vertices?filter=&limit=5000".format(tenant))

cluster_to_connected_vertex = defaultdict(set)
cluster_to_connected_documents = defaultdict(list)

kafka_topic_to_cluster = defaultdict(set)
kafka_topic_to_vertices = defaultdict(list)

collector_id = "collector_id"

for raw_vertex in raw_vertices:
    vertex_type = raw_vertex["_type"]

    if vertex_type not in ("AWS_Instance",):
        continue

    tags = raw_vertex.get("tags", {})
    environment = tags.get("environment")
    if environment and environment.lower().find("prod") == -1:
        # process only production
        continue

    vertex_keys = raw_vertex["_keys"]
    vertex_name = raw_vertex["_name"]
    # if auto scaling group defined - connect the cluster to the auto scaling

    auto_scaling_group_name = tags.get("aws:autoscaling:groupName")
    connected_vertex = auto_scaling_group_name if auto_scaling_group_name else vertex_keys.values()[0]

    # if create kafak topic vertex between the Kafka Cluster and the logengine and the archiver
    kafka_topic = tags.get("kafka_topic")
    kafka_topics = kafka_topic.split(",") if kafka_topic else []

    # collect cluster this instance belong to
    clusters = {}
    for tag_key, tag_value in tags.iteritems():
        if tag_key.find("-cluster") > -1:
            clusters[tag_key] = tag_value

    if clusters:
        for cluster_key, cluster_value in clusters.iteritems():
            cluster = "{}-{}".format(cluster_key, cluster_value)
            cluster_to_connected_vertex[cluster].add((connected_vertex, auto_scaling_group_name))
            cluster_to_connected_documents[cluster].append(raw_vertex)

            for kafka_topic in kafka_topics:
                kafka_topic_to_cluster[kafka_topic].add(cluster)

    else:
        # some instance missing cluster tag, for now fixing only logengine and archiver with PROD-incoming-:
        cluster_index = vertex_name.find("PROD-incoming-")
        if cluster_index > -1:
            for role in ("logengine", "archiver"):
                index = vertex_name.find(role)
                if index > -1:
                    cluster = "{}-{}".format(role, vertex_name[cluster_index + 14:index - 1])
                    cluster_to_connected_vertex[cluster].add((connected_vertex, auto_scaling_group_name))
                    cluster_to_connected_documents[cluster].append(raw_vertex)
                    for kafka_topic in kafka_topics:
                        kafka_topic_to_cluster[kafka_topic].add(connected_vertex)

        elif vertex_name.find("haproxy") > -1:
            itsdk.connect(collector_id=collector_id, source=vertex_keys, target="kafkazk-cluster-1", topology="haproxy")
        else:
            for kafka_topic in kafka_topics:
                kafka_topic_to_vertices[kafka_topic].append(connected_vertex)

for name, connected_vertices in cluster_to_connected_vertex.iteritems():
    data = common_document(cluster_to_connected_documents[name])
    vertex = itsdk.add_vertex(collector_id=collector_id,
                              vertex_type="Cluster",
                              name=name,
                              keys=name,
                              data=data)

    for connected_vertex, auto_scaling_group_name in connected_vertices:
        topology = "asg-uses" if auto_scaling_group_name else "ec2-uses"
        itsdk.connect(collector_id=collector_id, source=vertex, target=connected_vertex, topology=topology)

all_kafka_topics = set().union(kafka_topic_to_vertices.keys()).union(kafka_topic_to_cluster.keys())
all_clusters = set(cluster_to_connected_vertex.keys())
for kafka_topic in all_kafka_topics:
    vertex = itsdk.add_vertex(collector_id=collector_id,
                              vertex_type="Kafka_Topic",
                              name=kafka_topic,
                              keys=kafka_topic)

    itsdk.connect(collector_id=collector_id,
                  source="kafkazk-cluster-1",
                  target=kafka_topic,
                  topology=kafka_topic)

    logengine_cluster = kafka_topic.replace("incoming-", "logengine-")
    archiver_cluster = kafka_topic.replace("incoming-", "archiver-")
    es_cluster = kafka_topic.replace("incoming-", "es-")
    if logengine_cluster in all_clusters:
        itsdk.connect(collector_id=collector_id,
                      source=kafka_topic,
                      target=logengine_cluster,
                      topology="logengine")
        if es_cluster in all_clusters:
            itsdk.connect(collector_id=collector_id,
                          source=logengine_cluster,
                          target=es_cluster,
                          topology="es")

    if archiver_cluster in all_clusters:
        itsdk.connect(collector_id=collector_id,
                      source=kafka_topic,
                      target=archiver_cluster,
                      topology="archiver")


itsdk.flush_all()
