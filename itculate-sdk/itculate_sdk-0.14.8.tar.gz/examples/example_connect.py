import itculate_sdk as itsdk

itsdk.init(server_url="http://localhost:5000/api/v1")

id = "connect_id"

cassandras = ["cassandra|i-d67c2b4d", "cassandra|i-86886002", "cassandra|i-92d6d912"]
elb_ec2 = ["i-fbf1c1f5", "i-0127df207dc54d1ad"]

itsdk.connect(collector_id=id,
              source=elb_ec2,
              target=cassandras,
              topology="read")

cassandra_cluster = itsdk.add_vertex(collector_id=id, keys="Cassandras-Cluster", name="Cassandras",
                                     vertex_type="Cluster")
itsdk.connect(collector_id=id, source=cassandra_cluster, target=cassandras, topology="uses")


itsdk.enable_grouper_algorithm(group_vertex_type=cassandra_cluster.type,
                               member_vertex_type="Cassandra",
                               topology="uses")

itsdk.flush_all()
