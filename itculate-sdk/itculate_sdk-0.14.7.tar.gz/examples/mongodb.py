import datetime
import random
from examples.util import Service, mockup_samples

import itculate_sdk as itsdk

from unix_dates import UnixDate, UnixTimeDelta

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    cid = "ontap_cloud"

    mongodb_primary = itsdk.add_vertex(collector_id=cid,
                                       name="MongoDB Primary",
                                       vertex_type="AWS_Instance",
                                       keys="{}-MongoDB-Primary".format(cid),
                                       _subtype="MongoDB",
                                       data={
                                           "instance-id": "i-661134511",
                                           "instance-type": "m4.4xlarge",
                                           "estimated-cost": 532.16,
                                           "availability-zone": "us-east-1b"
                                       })

    mongodb_secondary_0 = itsdk.add_vertex(collector_id=cid,
                                           name="MongoDB Secondary-0",
                                           vertex_type="AWS_Instance",
                                           _subtype="MongoDB",
                                           keys="{}-MongoDB-Secondary-0".format(cid),
                                           data={
                                               "instance-id": "i-661134512",
                                               "instance-type": "m4.4xlarge",
                                               "estimated-cost": 532.16,
                                               "availability-zone": "us-east-1c"
                                           })

    mongodb_secondary_1 = itsdk.add_vertex(collector_id=cid,
                                           name="MongoDB Secondary-1",
                                           vertex_type="AWS_Instance",
                                           _subtype="MongoDB",
                                           keys="{}-MongoDB-Secondary-1".format(cid),
                                           data={
                                               "instance-id": "i-661134513",
                                               "instance-type": "m4.4xlarge",
                                               "estimated-cost": 532.16,
                                               "availability-zone": "us-east-1d"
                                           })

    itsdk.connect(source=mongodb_primary,
                  target=[mongodb_secondary_0, mongodb_secondary_1],
                  topology="replica",
                  collector_id=cid)

    cms_service = Service.create_service(key_prefix=cid,
                                         name="content-management-service",
                                         collector_id=cid,
                                         rds_count=1,
                                         ec2_count=6)

    itsdk.connect(source=cms_service.ec2s,
                  target=[mongodb_primary, mongodb_secondary_0, mongodb_secondary_1],
                  topology="use-mongodb",
                  collector_id=cid)

    end_time = UnixDate.now()
    start_time = end_time - UnixTimeDelta.calc(hours=24)
    fix_time = end_time - UnixTimeDelta.calc(hours=12)

    print cms_service.ec2s[0]

    itsdk.flush_all()

    for timestamp in range(int(start_time), int(end_time), 15):
        ec2_cpu_utilization = random.randint(80, 98) / 100.0
        network_throughput = ec2_cpu_utilization * 12 * 1024.0  # MB
        mongo_cpu_utilization = ec2_cpu_utilization / 8.0
        latency = ec2_cpu_utilization * random.randint(10000, 10100)
        if timestamp > fix_time:
            ec2_cpu_utilization /= 9.1
            network_throughput /= 1024.0
            mongo_cpu_utilization *= 1.75
            latency /= 100.0

        # itsdk.add_sample(vertex=cms_service.asg,
        #                  timestamp=timestamp,
        #                  counter="cpu-utilization",
        #                  value=itsdk.CPUPercentDataType.value(value=ec2_cpu_utilization, importance=2))

        itsdk.add_sample(vertex=cms_service.asg,
                         timestamp=timestamp,
                         counter="network",
                         value=itsdk.NetworkThroughputDataType.value(value=network_throughput, importance=3))

        # itsdk.add_sample(vertex=mongodb_primary,
        #                  timestamp=timestamp,
        #                  counter="cpu-utilization",
        #                  value=itsdk.CPUPercentDataType.value(value=mongo_cpu_utilization, importance=2))
        #
        # itsdk.add_sample(vertex=cms_service.elb,
        #                  timestamp=timestamp,
        #                  counter="latency",
        #                  value=itsdk.LatencyDataType.value(value=latency, importance=1))

    itsdk.flush_all()

