#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#
from examples import util

import itculate_sdk as itsdk

id = "localytics"
topology = "payload-processing"


if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    # https://aws.amazon.com/solutions/case-studies/localytics/

    elb = itsdk.add_vertex(collector_id=id, name="elb", vertex_type="AWS_ELB", keys="elb")
    queue = itsdk.add_vertex(collector_id=id, name="Queue", vertex_type="AWS_SQS", keys="Queue")
    asg = itsdk.add_vertex(collector_id=id, name="Processing Service", vertex_type="AWS_Auto_Scaling_Group", keys="asg")
    rds = itsdk.add_vertex(collector_id=id, name="db1", vertex_type="AWS_DynamoDB", keys="db1")
    kinesis = itsdk.add_vertex(collector_id=id, name="kinesis", vertex_type="AWS_Kinesis", keys="kinesis")

    ec2s = [
        itsdk.add_vertex(collector_id=id,
                         name="i-d67c1bg{}".format(i),
                         vertex_type="AWS_Instance",
                         keys="i-d67c1bg{}".format(i))
        for i in range(8)
        ]

    lambda_services = [
        itsdk.add_vertex(collector_id=id,
                         name="lambda-services-{}".format(i),
                         vertex_type="AWS_Lambda",
                         keys="lambda-services-{}".format(i))
        for i in range(1, 5)
        ]

    itsdk.connect(collector_id=id, source=elb, target=queue, topology=topology)
    itsdk.connect(collector_id=id, source=queue, target=asg, topology=topology)
    itsdk.connect(collector_id=id, source=asg, target=rds, topology="rds")
    itsdk.connect(collector_id=id, source=asg, target=kinesis, topology=topology)

    for ec2 in ec2s:
        itsdk.connect(collector_id=id, source=asg, target=ec2, topology="ec2")

    for lambda_service in lambda_services:
        itsdk.connect(collector_id=id, source=kinesis, target=lambda_service, topology=topology)

    util.mockup_samples(lambda_services + [rds] + [asg])

    itsdk.vertex_unhealthy(collector_id=id,
                           vertex=lambda_services[1],
                           message="Failed to pull from Kinesis stream")

    itsdk.flush_all()
