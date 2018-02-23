import random
from unix_dates import UnixDate, UnixTimeDelta

__author__ = 'ran'

import itculate_sdk as itsdk

api_key = "6AcMQbkd75yoJKmmKFVBQs7q1jkq9j8c"
api_secret = "B8d9tLv8eItzWINE02RhY6mCPsDne_L_NIDypE26yK7r_yj8WC_nf2zjJ2l1EHTT"
server_url = "https://api.itculate.io/api/v1"
itsdk.init(server_url=server_url, api_secret=api_secret, api_key=api_key)
#
# itsdk.init(server_url="http://localhost:5000/api/v1")

collector_id = "nipendo"

topology = "business-process-high-level"

application_source = itsdk.add_vertex(
    collector_id=collector_id,
    name="Application-Source",
    vertex_type="Adapter",
    keys="application-source-adapter",
    Description="Identify business process event and send them")
source_to_normalized = itsdk.add_vertex(
    collector_id=collector_id,
    name="Source-To-Normalized",
    vertex_type="Translator",
    keys="source-to-normalized",
    Description="Normalize the data to Nipendo format")
rule_engine = itsdk.add_vertex(
    collector_id=collector_id,
    name="Rule-Engine",
    vertex_type="BPM",
    keys="bpm",
    Description="Identify the next steps in the business process")
normalized_to_target = itsdk.add_vertex(
    collector_id=collector_id,
    name="Normalized-To-Target",
    vertex_type="Translator",
    keys="normalized-to-target",
    Description="Translate data to Application format")
application_target = itsdk.add_vertex(
    collector_id=collector_id,
    name="Application-Target",
    vertex_type="Adapter",
    keys="application-target-adapter",
    Description="Notify a business event to the target Application")
email = itsdk.add_vertex(
    collector_id=collector_id,
    name="Email",
    vertex_type="Adapter",
    keys="email-adapter",
    Description="send e-mail notification")
user_confirmation = itsdk.add_vertex(
    collector_id=collector_id,
    name="User-Confirmation",
    vertex_type="Adapter",
    keys="user-confirmation",
    Description="Wait for user confirmation")

database = itsdk.add_vertex(
    collector_id=collector_id,
    name="MsSQL",
    vertex_type="Database",
    keys="Database",
    Description="Database")

itsdk.connect(collector_id=collector_id, source=application_source, target=source_to_normalized, topology=topology)
itsdk.connect(collector_id=collector_id, source=source_to_normalized, target=rule_engine, topology=topology)
itsdk.connect(collector_id=collector_id, source=rule_engine, target=normalized_to_target, topology=topology)
itsdk.connect(collector_id=collector_id, source=normalized_to_target, target=application_target, topology=topology)
itsdk.connect(collector_id=collector_id, source=normalized_to_target, target=user_confirmation, topology=topology)
itsdk.connect(collector_id=collector_id, source=normalized_to_target, target=email, topology=topology)

itsdk.connect(collector_id=collector_id, source=rule_engine, target=database, topology="database")

# flush topology
itsdk.flush_all()

event_time = None
now = UnixDate.now() - UnixTimeDelta.calc(hours=24)
for key in ["bpm", "user-confirmation", "email-adapter", "application-target-adapter"]:
    for i in range(24 * 60):
        timestamp = now + UnixTimeDelta.calc(minutes=i)

        transaction = 3 + 100 * random.random()
        duration = 110 + 1000 * random.random()

        if i == 600:
            event_time = timestamp
            transaction = 2
            duration = 3012

        itsdk.add_sample(vertex=key,
                         timestamp=timestamp,
                         counter="transaction",
                         value=itsdk.QueueSizeDataType.value(transaction))

        itsdk.add_sample(vertex=key,
                         timestamp=timestamp,
                         counter="duration",
                         value=itsdk.LatencyDataType.value(duration))

# flush time series
itsdk.flush_all()

itsdk.vertex_unhealthy(collector_id=collector_id,
                       vertex="email-adapter",
                       message="Failed to connect to mail server transaction T133-1944",
                       timestamp=event_time)
itsdk.flush_all()
