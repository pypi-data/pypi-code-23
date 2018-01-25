import itculate_sdk as itsdk

api_key = "TtgEtruczJxh0hZYFhB5Dv8gH32BnqwG"
api_secret = "EEjn0P7WtsgidFK5kEhZo4sH53yyG-F6FzGD80dnlb9hBMIsshsUazf8rNKVuOt9"
tenant_id = "4UrA3vg3zN7hrVQtlMfFRo"
collector_id = "jobcase_test"

itsdk.init(api_key=api_key, api_secret=api_secret)
# itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)

# muninn clusters
muninn_util_1 = "i-0cac5593c1fe67d87"
muninn_util_2 = "i-057f314180ab482dc"

muninn_util_instances = [
    "i-b3f6fba5",  # util-04
    "i-ed74ce7e",  # util-05
    "i-bc44fe2f",  # util-06
    "i-b744fe24",  # util-07
    "i-a345ff30",  # util-08
    "i-f545ff66",  # util-09
    "i-7374cee0",  # util-10
    "i-f83a806b",  # util-11
    "i-5845ffcb",  # util-12
    "i-036cd690",  # util-13
]

muninn_job_listing_instances = [
    "i-08d29c8674ef220ee",
    "i-07a7dcf1a20a7d2ef",
    "i-05ad930afe71b2b03",
    "i-0c19388adc0f97d64",
    "i-06e7c2817afddd130",
    "i-08990bbcd4255bd22",
    "i-03eb2763abd6c5986",
    "i-0da94402d3e6542eb",
    "i-0448087d517abfc8e",
    "i-03c921e2217e4bda1"
]

muninn_api_instances = [
    "i-41fc5c40",  # api-01
    "i-1bd70b88",  # api-02
]

# RDS
rds_muninn_db = "arn:aws:rds:us-east-1:874501153367:db:muninn-db"
rds_scheduler = "arn:aws:rds:us-east-1:491834291579:db:scheduler"
rds_snorta_db = "arn:aws:rds:us-east-1:874501153367:db:snotra-db"

# Connect the muninn clusters to (RDS)
itsdk.connect(collector_id=collector_id,
              source=muninn_util_2,
              target=[rds_muninn_db, rds_scheduler],
              topology="dependency")

# Connect the muninn API cluster to the EC2 instances
itsdk.connect(collector_id=collector_id,
              source=[rds_muninn_db, rds_scheduler],
              target=muninn_api_instances,
              topology="dependency")

muninn_topic_profile = itsdk.add_vertex(collector_id=collector_id,
                                        name="Profile",
                                        vertex_type="Topic",
                                        keys="com.p11a.views.Profile")

muninn_topic_util = itsdk.add_vertex(collector_id=collector_id,
                                     name="Jobcase",
                                     vertex_type="Topic",
                                     keys="com.p11a.views.Conversations-com.p11a.views.Comments")

muninn_stream_profiles = []
muninn_stream_utils = []

for i in range(4, 14):
    # Create and connect the profile stream
    profile_name = "muninnProfile{:02}".format(i)
    profile_vertex = itsdk.add_vertex(collector_id=collector_id,
                                      name=profile_name,
                                      vertex_type="Snotra Stream",
                                      keys="{}-efc9a3045270c7d704114556d360722c".format(profile_name))

    itsdk.connect(collector_id=collector_id,
                  source=muninn_topic_profile,
                  target=profile_vertex,
                  topology="grouping")

    itsdk.connect(collector_id=collector_id,
                  source=muninn_util_instances[i - 4],
                  target=profile_vertex,
                  topology="dependency")

    muninn_stream_profiles.append(profile_vertex)

    # Create and connect the util stream
    util_name = "muninnUtil{:02}".format(i)
    util_vertex = itsdk.add_vertex(collector_id=collector_id,
                                   name=util_name,
                                   vertex_type="Snotra Stream",
                                   keys="{}-ee0d5380fd15e92b69b9c5cef48ddc06".format(util_name))

    itsdk.connect(collector_id=collector_id,
                  source=muninn_topic_util,
                  target=util_vertex,
                  topology="grouping")

    itsdk.connect(collector_id=collector_id,
                  source=muninn_util_instances[i - 4],
                  target=util_vertex,
                  topology="dependency")

    muninn_stream_utils.append(util_vertex)

# Connect the muninn util cluster to the EC2 instances
muninn_common_dependencies = [
    rds_muninn_db,
    rds_scheduler,
    rds_snorta_db,
    "arn:aws:rds:us-east-1:491834291579:db:odin-profile-db-mirror",
    "arn:aws:rds:us-east-1:491834291579:db:jobcase-prod-mirror",
    muninn_topic_util,
    muninn_topic_profile,
    "arn:aws:kinesis:us-east-1:874501153367:stream/muninn-production-InterestPoolUpsertProcessingJob"
]

# Connect each of the util instance to their dependencies
itsdk.connect(collector_id=collector_id,
              source=muninn_util_instances,
              target=muninn_common_dependencies,
              topology="dependency")

# Connect each of the joblisting to their dependencies
itsdk.connect(collector_id=collector_id,
              source=muninn_job_listing_instances,
              target=muninn_common_dependencies,
              topology="dependency")
itsdk.connect(collector_id=collector_id,
              source=muninn_job_listing_instances,
              target="arn:aws:kinesis:us-east-1:874501153367:stream/bragi-production-NovelJobListings",
              topology="dependency")

# connect the joblistings kinesis vertex to joblistings cluster
itsdk.connect(collector_id=collector_id,
              source=muninn_util_2,
              target="arn:aws:kinesis:us-east-1:874501153367:stream/muninn-production-InterestPoolUpsertProcessingJob",
              topology="dependency")

# Snotra infrastructure
snotra_relay_profile = itsdk.add_vertex(collector_id=collector_id,
                                        name="profile-binlog",
                                        vertex_type="Snotra Relay",
                                        keys="snotra-relay:profile-binlog")
snotra_relay_jobcase = itsdk.add_vertex(collector_id=collector_id,
                                        name="jobcase-binlog",
                                        vertex_type="Snotra Relay",
                                        keys="snotra-relay:jobcase-binlog")
snotra_bootstrap_producer_profile = itsdk.add_vertex(collector_id=collector_id,
                                                     name="profile-binlog",
                                                     vertex_type="Snotra Bootstrap Producer",
                                                     keys="snotra-bootstrap-producer:profile-binlog")
snotra_bootstrap_producer_jobcase = itsdk.add_vertex(collector_id=collector_id,
                                                     name="jobcase-binlog",
                                                     vertex_type="Snotra Bootstrap Producer",
                                                     keys="snotra-bootstrap-producer:jobcase-binlog")

profile_db_databus_mirror = "i-cdcc78db"
jobcase_db_databus_mirror = "i-2c52cdb5"

itsdk.connect(collector_id=collector_id,
              source=profile_db_databus_mirror,
              target="arn:aws:rds:us-east-1:491834291579:db:odin-profile-db-prod",
              topology="dependency")
itsdk.connect(collector_id=collector_id, source=snotra_relay_profile,
              target=profile_db_databus_mirror, topology="dependency")
itsdk.connect(collector_id=collector_id, source=snotra_bootstrap_producer_profile,
              target=snotra_relay_profile, topology="dependency")

itsdk.connect(collector_id=collector_id, source=jobcase_db_databus_mirror,
              target="arn:aws:rds:us-east-1:491834291579:db:jobcase-prod", topology="dependency")
itsdk.connect(collector_id=collector_id, source=snotra_relay_jobcase,
              target=jobcase_db_databus_mirror, topology="dependency")
itsdk.connect(collector_id=collector_id, source=snotra_bootstrap_producer_jobcase,
              target=snotra_relay_jobcase, topology="dependency")

bootstrap_db = "arn:aws:rds:us-east-1:874501153367:db:databus-bootstrap-db"
itsdk.connect(collector_id=collector_id, source=snotra_bootstrap_producer_profile,
              target=bootstrap_db, topology="dependency")
itsdk.connect(collector_id=collector_id,
              source=snotra_bootstrap_producer_jobcase,
              target=bootstrap_db,
              topology="dependency")

# Muninn streams
itsdk.connect(collector_id=collector_id,
              source=muninn_stream_profiles,
              target=snotra_relay_jobcase,
              topology="dependency")

itsdk.connect(collector_id=collector_id,
              source=muninn_stream_profiles,
              target=snotra_relay_profile,
              topology="dependency")

# itsdk.vertex_unhealthy(vertex="i-b744fe24", message="Failed OMG!")
itsdk.vertex_unhealthy(collector_id=collector_id, vertex=snotra_relay_profile, message="Relay is DOWN!")
# itsdk.vertex_healthy(collector_id=collector_id, vertex=snotra_relay_profile)

itsdk.flush_all()
