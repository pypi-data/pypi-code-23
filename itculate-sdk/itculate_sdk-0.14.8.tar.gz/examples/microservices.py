#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

from examples.util import mockup_samples, Service

import itculate_sdk as itsdk

# please contact admin@itculate.io for api_key and api_secret

collector_id = "data_process_pipeline"
topology = "payload-processing"

vertices = {}

# rds_with_event = None
# asg_with_event = None
# service_with_event = None

if __name__ == '__main__':
    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:
    bucket = itsdk.add_vertex(collector_id=collector_id,
                              name="uploaded_bucket",
                              vertex_type="S3",
                              keys="uploaded-bucket")

    # Defining the first service:
    # Create the s3 Vertex:
    a_lambda = itsdk.add_vertex(collector_id=collector_id,
                                name="payload-uploaded",
                                vertex_type="Lambda",
                                keys="lambda-payload-uploaded")

    # create 4 Microservice
    normalizer = Service.create_service(name="normalizer", ec2_count=16, redis_count=1, rds_count=1,
                                        collector_id=collector_id)

    fraud_analyzer = Service.create_service(name="fraud-analyzer", ec2_count=12, redis_count=2, redshift_count=1,
                                            collector_id=collector_id)

    abnormal_detection = Service.create_service(name="abnormal-detection", ec2_count=4, redis_count=1, rds_count=1,
                                                collector_id=collector_id)

    event_distributer = Service.create_service(name="event-distributer", ec2_count=2, rds_count=1,
                                               collector_id=collector_id)

    # connect the  bucket to lambda to Microservice
    itsdk.connect(collector_id=collector_id,
                  source=bucket,
                  target=a_lambda,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=a_lambda,
                  target=normalizer.service,
                  topology="normalizer-service")

    itsdk.connect(collector_id=collector_id,
                  source=normalizer.service,
                  target=fraud_analyzer.service,
                  topology="fraud-analyzer-service")

    itsdk.connect(collector_id=collector_id,
                  source=fraud_analyzer.service,
                  target=abnormal_detection.service,
                  topology="abnormal_detection-service")

    itsdk.connect(collector_id=collector_id,
                  source=fraud_analyzer.service,
                  target=event_distributer.service,
                  topology="event-distributer-service")

    # Flush and commit topology
    itsdk.flush_all()

    # mockup timeseries

    mockup_samples(
        vertices=normalizer.vertices + fraud_analyzer.vertices + abnormal_detection.vertices + event_distributer.vertices,
        rds_connection_utilization_vertices=[abnormal_detection.rdses[0],
                                             abnormal_detection.asg,
                                             abnormal_detection.service],
        hour_of_event=15)

    # Flush and commit timeseries
    itsdk.flush_all()
