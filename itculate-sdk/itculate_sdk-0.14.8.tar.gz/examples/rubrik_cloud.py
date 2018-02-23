import datetime
import random
from examples.util import Service, mockup_samples

import itculate_sdk as itsdk

from unix_dates import UnixDate, UnixTimeDelta

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    itsdk.init(role="cloudoscope")
    # itsdk.init(role="cloudoscope", server_url="http://localhost:5000/api/v1")

    cid = "rubrik_cloud"

    rubrik_nodes = []
    rubrik_nodes_ebses = []
    for i in range(1, 3):
        ec2 = itsdk.add_vertex(collector_id=cid,
                               name="i-{}61234331221 (Rubrik Node {})".format(i, i),
                               vertex_type="AWS_Instance",
                               keys="i-{}61234331221".format(i),
                               data={
                                   "instance-type": "c4.4xlarge",
                                   "estimated-cost": 632.16,
                                   "availability-zone": "us-east-1b"
                               })
        ebses = [itsdk.add_vertex(collector_id=cid,
                                  name="v-66123443{}{}".format(j, i),
                                  vertex_type="AWS_EBS_Volume",
                                  keys="v-66123443{}{}".format(j, i),
                                  data={
                                      "Capacity": 800,
                                      "availability-zone": "us-east-1b",
                                      "estimated-cost": 111.21,
                                  }
                                  ) for j in range(3)]

        rubrik_nodes_ebses += ebses
        itsdk.connect(source=ec2, target=ebses, topology="uses-ebs", collector_id=cid)
        rubrik_nodes.append(ec2)

    rubrik = itsdk.add_vertex(collector_id=cid,
                              name="app-backup-prod",
                              vertex_type="Rubrik",
                              keys="Rubrik.prod",
                              data={
                                  "estimated-cost": 2928.96,
                                  "Version": "9.0.1",
                                  "availability-zone": "us-east-1b"
                              })

    rubrik_clients = [itsdk.add_vertex(collector_id=cid,
                                       name="i-61234331225{} (Client {})".format(i, i+1),
                                       vertex_type="AWS_Instance",
                                       keys="i-61234331225{}".format(i),
                                       data={
                                           "availability-zone": "us-east-1c",
                                           "estimated-cost": 31.14,
                                       }) for i in range(3)]

    itsdk.connect(source=rubrik_clients, target=rubrik, topology="uses", collector_id=cid)

    itsdk.connect(source=rubrik, target=rubrik_nodes, topology="deploy-on", collector_id=cid)

    vertices = []
    vertices += rubrik_clients + rubrik_nodes_ebses + rubrik_nodes + [rubrik]

    mockup_samples(vertices=vertices)

    itsdk.flush_all()
