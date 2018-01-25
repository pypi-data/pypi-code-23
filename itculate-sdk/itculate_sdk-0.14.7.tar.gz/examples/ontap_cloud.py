import datetime
import random
from examples.util import Service, mockup_samples

import itculate_sdk as itsdk

from unix_dates import UnixDate, UnixTimeDelta

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(role="cloudoscope", server_url="http://localhost:5000/api/v1")

    cid = "ontap_cloud"

    ec2 = itsdk.add_vertex(collector_id=cid,
                           name="i-1234331221 (ONTAP 9)",
                           vertex_type="AWS_Instance",
                           keys="i-1234331221",
                           data={
                               "instance-type": "c4.4xlarge",
                               "estimated-cost": 632.16,
                               "availability-zone": "us-east-1b"
                           })
    ebses = [itsdk.add_vertex(collector_id=cid,
                              name="v-6123443{}".format(i),
                              vertex_type="AWS_EBS_Volume",
                              keys="v-6123443{}".format(i),
                              data={
                                  "Capacity": 800,
                                  "availability-zone": "us-east-1b",
                                  "estimated-cost": 111.21,
                              }
                              ) for i in range(5)]

    itsdk.connect(source=ec2, target=ebses, topology="uses-ebs", collector_id=cid)

    ontap = itsdk.add_vertex(collector_id=cid,
                             name="app-backup-prod",
                             vertex_type="Ontap_Cloud",
                             keys="ONTAP.prod",
                             data={
                                 "estimated-cost": 2928.96,
                                 "Version": "9.0.1",
                                 "availability-zone": "us-east-1b"
                             })

    netapp_volumes = [itsdk.add_vertex(collector_id=cid,
                                       name="volume-{}".format(i),
                                       vertex_type="NetApp_Volume",
                                       keys="volume-{}".format(i),
                                       data={
                                           "availability-zone": "us-east-1b"
                                       }
                                       ) for i in range(3)]

    netapp_volumes_clients = [itsdk.add_vertex(collector_id=cid,
                                               name="i-1234331225{} (Backup {})".format(i, i),
                                               vertex_type="AWS_Instance",
                                               keys="i-1234331225{}".format(i),
                                               data={
                                                   "availability-zone": "us-east-1c",
                                                   "estimated-cost": 31.14,
                                               }) for i in range(3)]

    for i in range(3):
        itsdk.connect(source=netapp_volumes_clients[i], target=netapp_volumes[i], topology="nfs", collector_id=cid)

    itsdk.connect(source=netapp_volumes, target=ontap, topology="uses-volume", collector_id=cid)

    itsdk.connect(source=ontap, target=ec2, topology="deploy-on", collector_id=cid)

    vertices = []
    vertices += netapp_volumes_clients + netapp_volumes + ebses + [ec2] + [ontap]

    mockup_samples(vertices=vertices,
                   feel_pain_vertices=[netapp_volumes[0]],
                   cause_pain_vertices=[netapp_volumes[1]],
                   contention_vertices=[ontap, ec2, ebses[0]])

    itsdk.flush_all()
