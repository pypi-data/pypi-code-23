from examples.util import Service

import itculate_sdk as itsdk
from unix_dates import UnixTimeDelta, UnixDate

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud
    itsdk.init(role="cloudoscope")
    # itsdk.init(role="cloudoscope", server_url="http://localhost:5000/api/v1")

    cid = "security_group"

    cidr_ipv4_1 = itsdk.add_vertex(collector_id=cid,
                                   name="211.211.10.30/16",
                                   vertex_type="CIDR-IPv4",
                                   keys="{}211.211.10.30/16".format(cid))

    cidr_ipv4_2 = itsdk.add_vertex(collector_id=cid,
                                   name="201.11.110.130/8",
                                   vertex_type="CIDR-IPv4",
                                   keys="{}201.11.110.130/8".format(cid))

    i = 4123451
    sg_jump_host = itsdk.add_vertex(collector_id=cid,
                                    name="sg-jump-host",
                                    vertex_type="AWS_Security_Group",
                                    keys="{}sg-{}".format(cid, i))

    i += 1
    sg_analytics = itsdk.add_vertex(collector_id=cid,
                                    name="sg-analytics",
                                    vertex_type="AWS_Security_Group",
                                    keys="{}sg-{}".format(cid, i))

    i += 1
    sg_dpp = itsdk.add_vertex(collector_id=cid,
                              name="sg-data-processing",
                              vertex_type="AWS_Security_Group",
                              keys="{}sg-{}".format(cid, i))

    i += 1
    sg_web_api = itsdk.add_vertex(collector_id=cid,
                                  name="sg-web-api",
                                  vertex_type="AWS_Security_Group",
                                  keys="{}sg-412345{}".format(cid, i))

    i += 1
    sg_users_rds = itsdk.add_vertex(collector_id=cid,
                                    name="sg-users-rds",
                                    vertex_type="AWS_Security_Group",
                                    keys="{}sg-{}".format(cid, i))

    i += 1
    sg_collectors_rds = itsdk.add_vertex(collector_id=cid,
                                         name="sg-collectors-rds",
                                         vertex_type="AWS_Security_Group",
                                         keys="{}sg-412345{}".format(cid, i))

    i += 1
    sg_devices_rds = itsdk.add_vertex(collector_id=cid,
                                      name="sg-devices-rds",
                                      vertex_type="AWS_Security_Group",
                                      keys="{}sg-{}".format(cid, i))

    i += 1
    sg_qa_rds_test = itsdk.add_vertex(collector_id=cid,
                                      name="sg-qa-rds-test",
                                      vertex_type="AWS_Security_Group",
                                      keys="{}sg-{}".format(cid, i))

    itsdk.connect(source=cidr_ipv4_1, target=sg_jump_host, topology="cidr_from:22-to:22", collector_id=cid)
    itsdk.connect(source=cidr_ipv4_2, target=sg_jump_host, topology="cidr_from:22-to:22", collector_id=cid)
    itsdk.connect(source=sg_jump_host, target=sg_analytics, topology="cidr_from:22-to:22", collector_id=cid)
    itsdk.connect(source=sg_jump_host, target=sg_dpp, topology="cidr_from:22-to:22", collector_id=cid)
    itsdk.connect(source=sg_jump_host, target=sg_web_api, topology="cidr_from:22-to:22", collector_id=cid)
    itsdk.connect(source=sg_analytics, target=sg_users_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_analytics, target=sg_collectors_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_analytics, target=sg_devices_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_dpp, target=sg_users_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_dpp, target=sg_devices_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_dpp, target=sg_collectors_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_web_api, target=sg_users_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_web_api, target=sg_devices_rds, topology="cidr_from:3306-to:3306", collector_id=cid)
    itsdk.connect(source=sg_web_api, target=sg_collectors_rds, topology="cidr_from:3306-to:3306", collector_id=cid)

    itsdk.connect(source=cidr_ipv4_2, target=sg_qa_rds_test, topology="cidr_from:3306-to:3306", collector_id=cid)

    devices_rds = itsdk.add_vertex(collector_id=cid,
                                   name="devices",
                                   vertex_type="AWS_Aurora",
                                   keys="{}devices".format(cid))

    users_rds = itsdk.add_vertex(collector_id=cid,
                                 name="users",
                                 vertex_type="AWS_RDS",
                                 keys="{}users".format(cid))

    collectors_rds = itsdk.add_vertex(collector_id=cid,
                                      name="collectors",
                                      vertex_type="AWS_RDS",
                                      keys="{}collectors".format(cid))

    itsdk.connect(source=sg_devices_rds, target=devices_rds, topology="sg-rds-member", collector_id=cid)
    itsdk.connect(source=sg_users_rds, target=users_rds, topology="sg-rds-member", collector_id=cid)
    itsdk.connect(source=sg_collectors_rds, target=collectors_rds, topology="sg-rds-member", collector_id=cid)

    itsdk.connect(source=sg_qa_rds_test, target=collectors_rds, topology="sg-rds-member", collector_id=cid)

    jump_host_instance = itsdk.add_vertex(collector_id=cid,
                                          name="jump-host",
                                          vertex_type="AWS_Instance",
                                          keys="{}jump-host".format(cid))

    analytics_instances = [itsdk.add_vertex(collector_id=cid,
                                            name="ec2 analytic-{}".format(i),
                                            vertex_type="AWS_Instance",
                                            keys="{}analytics-{}".format(cid, i)) for i in range(1, 4)]

    itsdk.connect(source=jump_host_instance, target=sg_jump_host, topology="sg-instance-member", collector_id=cid)
    itsdk.connect(source=analytics_instances, target=sg_analytics, topology="sg-instance-member", collector_id=cid)

    itsdk.vertex_event(collector_id=cid,
                       vertex=sg_qa_rds_test,
                       severity="WARNING",
                       message="Inbound CIDR rule added, 201.11.110.130/8 can accesses 'collectors' RDS "
                               "(from-port: 3306 to-port: 3306)",
                       event_type="ACCESS_UPDATE",
                       timestamp=UnixDate.now())

    itsdk.flush_all()
