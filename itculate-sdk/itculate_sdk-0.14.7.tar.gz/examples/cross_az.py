#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#
import datetime
import random
from examples.util import Service, mockup_samples

import itculate_sdk as itsdk

from unix_dates import UnixDate, UnixTimeDelta


# please contact admin@itculate.io for api_key and api_secret


class AvailabilityZoneInternalTrafficDataType(itsdk.ThroughputDataType):
    pass


class AvailabilityZoneCrossTrafficDataType(itsdk.ThroughputDataType):
    pass


class AvailabilityZoneExternalTrafficDataType(itsdk.ThroughputDataType):
    pass


if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:

    collector_id = "cross_az"

    cassandra_service = Service.create_service(key_prefix=collector_id,
                                               name="cassandra-service",
                                               collector_id=collector_id,
                                               ec2_count=3,
                                               ec2_vertex_subtype="Cassandra")

    dpp_service = Service.create_service(key_prefix=collector_id,
                                         name="data-process-pipeline-worker",
                                         collector_id=collector_id,
                                         ec2_count=24)

    analytics_service = Service.create_service(key_prefix=collector_id,
                                               name="analytics-worker",
                                               collector_id=collector_id,
                                               ec2_count=4)

    analytics_api_service = Service.create_service(key_prefix=collector_id,
                                                   name="analytics-api",
                                                   collector_id=collector_id,
                                                   ec2_count=2)

    itsdk.connect(collector_id=collector_id,
                  source=dpp_service.asg,
                  target=cassandra_service.ec2s,
                  topology="dpp-cassandra$group")

    itsdk.connect(collector_id=collector_id,
                  source=dpp_service.ec2s,
                  target=cassandra_service.ec2s,
                  topology="dpp-cassandra")

    itsdk.connect(collector_id=collector_id,
                  source=analytics_service.asg,
                  target=cassandra_service.ec2s,
                  topology="aggregator-cassandra$group")

    itsdk.connect(collector_id=collector_id,
                  source=analytics_service.ec2s,
                  target=cassandra_service.ec2s,
                  topology="aggregator-cassandra")

    itsdk.connect(collector_id=collector_id,
                  source=analytics_api_service.asg,
                  target=cassandra_service.ec2s,
                  topology="aggregator-cassandra$group")

    itsdk.connect(collector_id=collector_id,
                  source=analytics_api_service.ec2s,
                  target=cassandra_service.ec2s,
                  topology="aggregator-cassandra")

    date = datetime.datetime.now()
    date = date.replace(microsecond=0, second=0, minute=0)

    end_time = UnixDate.to_unix_time(date)
    start_time = end_time - UnixTimeDelta.calc(hours=72)

    timestamp_of_change = end_time - (end_time - start_time) / 2

    i = 0

    network_in_internal_az = 20
    network_out_internal_az = 0.3
    network_in_cross_az = network_in_internal_az * 4
    network_out_cross_az = network_out_internal_az * 4

    efs = itsdk.add_vertex(collector_id=collector_id,
                           vertex_type="AWS_EFS",
                           name="images",
                           keys="efs_images",
                           data={
                               "instance-type": "m4.2xlarge",
                               "estimated-cost": 561,
                               "capacity": 561 * 3,
                               "availability-zones": [{"zone-name": "us-east-1b"}, {"zone-name": "us-east-1c"}]
                           })
    test_ec2 = itsdk.add_vertex(collector_id=collector_id,
                                name="i-31443312 (Test)",
                                vertex_type="AWS_Instance",
                                keys="i-31443312 (Test)",
                                data={
                                    "instance-type": "m4.2xlarge",
                                    "estimated-cost": 216,
                                    "availability-zone": "us-east-1b"
                                })

    itsdk.connect(source=test_ec2, target=efs, topology="use-file-system", collector_id=collector_id)

    for ec2 in analytics_service.ec2s:
        itsdk.connect(source=ec2, target=efs, topology="use-file-system", collector_id=collector_id)

    vertex = analytics_service.asg
    # vertex = analytics_api_service.elb
    print vertex
    total_factor = 4

    interval = 5 * 60
    for timestamp in range(int(start_time), int(end_time), interval):
        i += interval
        factor = 1
        if i % 3600 == 0:
            factor = 2.66

        if timestamp < timestamp_of_change:
            counter_value_tuple = [("network-in-internal-az", factor * random.randint(20, 30) / 1.1),
                                   ("network-out-internal-az", factor * random.randint(5, 15) / 4.1),
                                   ("network-in-cross-az", factor * 4 * random.randint(20, 30) / 1.1),
                                   ("network-out-cross-az", factor * 4 * random.randint(5, 15) / 4.1),
                                   ("network-in-external", random.randint(10, 20) / 31.9),
                                   ("network-out-external", random.randint(10, 20) / 91.9)]
        else:
            counter_value_tuple = [("network-in-cross-az", factor * random.randint(20, 30) / 1.1),
                                   ("network-out-cross-az", factor * random.randint(5, 15) / 4.1),
                                   ("network-in-internal-az", factor * 4 * random.randint(20, 30) / 1.1),
                                   ("network-out-internal-az", factor * 4 * random.randint(5, 15) / 4.1),
                                   ("network-in-external", random.randint(10, 20) / 31.9),
                                   ("network-out-external", random.randint(10, 20) / 91.9)]

        for counter_name, value in counter_value_tuple:
            if counter_name.find("internal") > -1:
                data_type = AvailabilityZoneInternalTrafficDataType
            elif counter_name.find("cross") > -1:
                data_type = AvailabilityZoneCrossTrafficDataType
            else:
                data_type = AvailabilityZoneExternalTrafficDataType

            itsdk.add_sample(vertex=vertex,
                             timestamp=timestamp,
                             counter=counter_name,
                             value=data_type.value(value=value * total_factor, importance=15))

    # mockup_samples([analytics_service.elb, test_ec2], start_time=start_time, end_time=end_time)
    itsdk.flush_all()
