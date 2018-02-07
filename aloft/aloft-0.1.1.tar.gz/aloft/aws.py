import boto3
import os
import re
import time
import uuid
from aloft.output import print_action
from aloft import config
from botocore.exceptions import ClientError

credentials = {}
region = None


def get_vpc_by_name(vpc_name):
    client = get_ec2_client()
    vpc = None

    vpcs = client.describe_vpcs(
        Filters=[
            {'Name': 'tag-key', 'Values': ['Name']},
            {'Name': 'tag-value', 'Values': [vpc_name]}
        ]
    )

    if len(vpcs['Vpcs']) == 1:
        vpc = vpcs['Vpcs'][0]
        vpc['Name'] = vpc_name

    return vpc


def assume_role(role_name):
    global credentials
    roles = config.get_roles()
    role = roles.get(role_name, None)

    os.environ['AWS_PROFILE'] = config.get_profile()
    if role and role.get('arn', None):
        client = get_sts_client()
        assumed_role = client.assume_role(
            RoleArn=role['arn'],
            RoleSessionName=role_name
        )
        set_credentials(assumed_role['Credentials'])
        set_region(role.get('region', 'us-east-1'))
    else:
        raise KeyError(f'Unable to find role {role_name}')


def set_credentials(new_credentials):
    global credentials
    credentials = new_credentials
    os.environ['AWS_ACCESS_KEY_ID'] = credentials['AccessKeyId']
    os.environ['AWS_SECRET_ACCESS_KEY'] = credentials['SecretAccessKey']
    os.environ['AWS_SESSION_TOKEN'] = credentials['SessionToken']


def set_region(new_region):
    global region
    region = new_region
    os.environ['AWS_REGiON'] = region


def delete_ec2_tags(resource_id, keys_to_delete):
    client = get_ec2_client()
    tags = []

    for key in keys_to_delete:
        tags.append({'Key': key})

    client.delete_tags(Resources=[resource_id], Tags=tags)


def create_ec2_tags(resource_id, tags_to_create_dictionary):
    client = get_ec2_client()
    tags = []

    for key, value in tags_to_create_dictionary.items():
        tags.append({'Key': key, 'Value': value})

    client.create_tags(Resources=[resource_id], Tags=tags)


def save_content_to_s3(content, bucket_name, key):
    bucket = get_or_create_s3_bucket(bucket_name)
    bucket.put_object(Body=content, Key=key)


def get_content_from_s3(bucket_name, key):
    s3 = get_s3_resource()
    s3_object = s3.Object(bucket_name, key)
    content = None

    try:
        content = s3_object.get()['Body'].read().decode('utf-8')
    except s3.meta.client.exceptions.NoSuchKey:
        pass
    except s3.meta.client.exceptions.NoSuchBucket:
        pass

    return content


def delete_file_in_s3(bucket_name, key):
    bucket = get_s3_bucket(bucket_name)
    objects_to_delete = {'Objects': [{'Key': key}]}
    bucket.delete_objects(Delete=objects_to_delete)


def get_or_create_s3_bucket(bucket_name):
    bucket = get_s3_bucket(bucket_name)

    if not bucket:
        create_s3_bucket(bucket_name)
        bucket = get_s3_bucket(bucket_name)

    return bucket


def get_s3_bucket(bucket_name):
    buckets = get_all_buckets()
    filtered_buckets = list(filter(lambda x: x.name == bucket_name, buckets))
    bucket = None

    if len(filtered_buckets) == 1:
        bucket = filtered_buckets[0]

    return bucket


def create_s3_bucket(bucket_name):
    s3 = get_s3_resource()
    session = boto3.session.Session()
    region = session.region_name

    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})


def get_all_buckets():
    s3 = get_s3_resource()
    return s3.buckets.all()


def get_vpn_gateway_id(vpn_name):
    vpn_gateway_id = None
    vpn_gateway = get_vpn_gateway(vpn_name)

    if vpn_gateway:
        vpn_gateway_id = vpn_gateway['VpnGatewayId']

    return vpn_gateway_id


def get_vpn_gateway_attachment_status(vpc):
    aws_vpc_id = vpc['VpcId']
    vpn_gateway = get_vpn_gateway(vpc['Name'])
    status = None

    if vpn_gateway:
        vpn_attachments = vpn_gateway.get('VpcAttachments', None)

        filtered_vpn_attachments = list(filter(lambda attachment: attachment['VpcId'] == aws_vpc_id, vpn_attachments))

        if filtered_vpn_attachments and len(filtered_vpn_attachments) == 1:
            status = filtered_vpn_attachments[0]['State']

    return status


def get_vpn_gateway(vpn_name):
    client = get_ec2_client()
    vpn_gateway = None

    vpn_gateways = client.describe_vpn_gateways(
        Filters=[
            {'Name': 'tag-key', 'Values': ['Name']},
            {'Name': 'tag-value', 'Values': [f'{vpn_name}-network']}
        ]
    )

    if len(vpn_gateways['VpnGateways']) == 1:
        vpn_gateway = vpn_gateways['VpnGateways'][0]

    return vpn_gateway


def get_route_table_ids(cluster_id):
    client = get_ec2_client()
    route_table_ids = None

    route_tables = client.describe_route_tables(
        Filters=[
            {'Name': 'tag-key', 'Values': ['KubernetesCluster']},
            {'Name': 'tag-value', 'Values': [cluster_id]}
        ]
    )

    if len(route_tables['RouteTables']) > 0:
        route_table_ids = list(map(lambda route_table: route_table['RouteTableId'], route_tables['RouteTables']))

    return route_table_ids


def propagate_route_table(route_table_id, vpn_gateway_id):
    print_action(f'Propagating route table: {route_table_id} {vpn_gateway_id}')

    client = get_ec2_client()
    client.enable_vgw_route_propagation(
        GatewayId=vpn_gateway_id,
        RouteTableId=route_table_id
    )


def set_role_policy(role_name, policy_name, policy_document):
    print_action(f'Setting role policy: {role_name} {policy_name}')

    client = get_iam_client()
    client.put_role_policy(
        RoleName=role_name,
        PolicyName=policy_name,
        PolicyDocument=policy_document
    )


def conditionally_create_hosted_zone_and_setup_ns_records(hosted_zone_to_create, parent_hosted_zone):
    hosted_zone = get_hosted_zone(hosted_zone_to_create)

    if not hosted_zone:
        print_action(f'Creating hosted zone: {hosted_zone_to_create}')
        new_hosted_zone = create_hosted_zone(hosted_zone_to_create)
        setup_ns_records_in_parent_domain(hosted_zone_to_create, parent_hosted_zone, new_hosted_zone)
    else:
        print_action(f'Hosted zone for {hosted_zone_to_create} already exists.  Not recreating hosted DNS zone.')


def setup_ns_records_in_parent_domain(cluster_id, vpc_id, child_hosted_zone):
    vpc_hosted_zone = get_hosted_zone(vpc_id)
    add_ns_records_to_hosted_zone(vpc_hosted_zone['Id'], cluster_id, child_hosted_zone['DelegationSet']['NameServers'])


def get_hosted_zone(domain):
    client = get_route53_client()
    hosted_zone = None

    hosted_zones = client.list_hosted_zones_by_name(
        DNSName=domain,
        MaxItems='1'
    )

    if (len(hosted_zones['HostedZones']) == 1 and
            re.match(f'{domain}[.]?', hosted_zones['HostedZones'][0]['Name']) is not None):
        hosted_zone = hosted_zones['HostedZones'][0]

    return hosted_zone


def create_hosted_zone(domain):
    client = get_route53_client()
    return client.create_hosted_zone(Name=domain, CallerReference=f'{uuid.uuid4()}')


def add_ns_records_to_hosted_zone(hosted_zone_id, record_set_name, ns_records):
    client = get_route53_client()
    resource_records = list(map(lambda record: {'Value': record}, ns_records))

    client.change_resource_record_sets(
        HostedZoneId=hosted_zone_id,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': record_set_name,
                        'Type': 'NS',
                        'TTL': 300,
                        'ResourceRecords': resource_records
                    }
                },
            ]
        }
    )


def create_vpc(vpc_name, cidr_block):
    print_action(f'Creating VPC {vpc_name} using CIDR {cidr_block}')
    client = get_ec2_client()
    response = client.create_vpc(
        CidrBlock=cidr_block,
    )

    vpc = response.get('Vpc', None)

    if vpc:
        vpc['Name'] = vpc_name
        create_ec2_tags(vpc['VpcId'], {'Name': vpc_name})

    return vpc


def create_and_attach_internet_gateway(vpc):
    internet_gateway = create_internet_gateway(vpc['Name'])
    attach_internet_gateway_to_vpc(internet_gateway, vpc)


def create_internet_gateway(vpc_name):
    print_action(f'Creating internet gateway for {vpc_name}')
    client = get_ec2_client()
    response = client.create_internet_gateway()

    internet_gateway = response.get('InternetGateway', None)

    if internet_gateway:
        create_ec2_tags(internet_gateway['InternetGatewayId'], {'Name': vpc_name})

    return internet_gateway


def attach_internet_gateway_to_vpc(internet_gateway, vpc):
    print_action('Attaching internet gateway to vpc.')
    client = get_ec2_client()
    client.attach_internet_gateway(
        InternetGatewayId=internet_gateway['InternetGatewayId'],
        VpcId=vpc['VpcId']
    )


def create_vpn_gateway(vpc_name):
    client = get_ec2_client()
    response = client.create_vpn_gateway(
        Type='ipsec.1',
    )

    vpn_gateway = response.get('VpnGateway', None)

    if vpn_gateway:
        create_ec2_tags(
            vpn_gateway['VpnGatewayId'],
            {
                'Name': f'{vpc_name}-network',
                'transitVPC1:preferred-path': 'CSR1',
                'transitVPC1:spoke': 'true',
            }
        )

    return vpn_gateway


def create_and_attach_vpn_gateway(vpc):
    vpn_gateway = get_vpn_gateway(vpc['Name'])

    if not vpn_gateway:
        print_action('Creating vpn gateway.')
        vpn_gateway = create_vpn_gateway(vpc['Name'])

    attach_vpn_gateway_and_wait_until_ready(vpn_gateway, vpc)


def attach_vpn_gateway_and_wait_until_ready(vpn_gateway, vpc):
    attach_vpn_gateway(vpn_gateway, vpc)
    print_action('Waiting for vpn gateway to attach to vpc.')
    time.sleep(20)

    while get_vpn_gateway_attachment_status(vpc) != 'attached':
        print('.', end='', flush=True)
        time.sleep(10)

    print(' attached\n')


def attach_vpn_gateway(vpn_gateway, vpc):
    client = get_ec2_client()
    response = None
    state = None

    try:
        response = client.attach_vpn_gateway(
            VpnGatewayId=vpn_gateway['VpnGatewayId'],
            VpcId=vpc['VpcId']
        )
    except ClientError as error:
        if error.response['Error']['Code'] != 'InvalidVpcID.NotFound':
            print(error)
            raise error

    if response:
        attachment = response.get('VpcAttachment', {'State': None})
        state = attachment['State']

    return state


def delete_network_and_vpc(vpc_name):
    vpc = get_vpc_by_name(vpc_name)
    vpn_gateway = get_vpn_gateway(vpc_name)
    vpn_connections = get_vpn_connections(vpn_gateway)
    internet_gateway = get_internet_gateway(vpc_name)

    remove_vpn_gateway_tags(vpn_gateway)
    detach_vpn_gateway_and_wait_until_detached(vpn_gateway, vpc)
    delete_vpn_connections(vpn_connections)
    delete_vpn_gateway(vpn_gateway)
    detach_internet_gateway(internet_gateway, vpc)
    delete_internet_gateway(internet_gateway)
    delete_vpc(vpc)


def get_vpn_connections(vpn_gateway):
    vpn_connections = None

    if vpn_gateway:
        client = get_ec2_client()
        response = client.describe_vpn_connections(
            Filters=[
                {
                    'Name': 'vpn-gateway-id',
                    'Values': [
                        vpn_gateway['VpnGatewayId'],
                    ]
                },
            ]
        )

        vpn_connections = response.get('VpnConnections', None)

    return vpn_connections


def delete_vpn_connections(vpn_connections):
    if vpn_connections:
        client = get_ec2_client()
        for vpn_connection in vpn_connections:
            print_action(f'Deleting VPN connection: {vpn_connection["VpnConnectionId"]}')
            client.delete_vpn_connection(
                VpnConnectionId=vpn_connection['VpnConnectionId']
            )


def delete_vpn_gateway(vpn_gateway):
    if vpn_gateway:
        print_action(f'Deleting VPN gateway: vpn_gateway["VpnGatewayId"]')
        client = get_ec2_client()
        client.delete_vpn_gateway(
            VpnGatewayId=vpn_gateway['VpnGatewayId']
        )


def get_internet_gateway(name):
    client = get_ec2_client()
    internet_gateway = None
    response = client.describe_internet_gateways(
        Filters=[
            {'Name': 'tag-key', 'Values': ['Name']},
            {'Name': 'tag-value', 'Values': [name]}
        ]
    )

    internet_gateways = response.get('InternetGateways', None)

    if internet_gateways and len(internet_gateways) == 1:
        internet_gateway = internet_gateways[0]

    return internet_gateway


def detach_internet_gateway(internet_gateway, vpc):
    if vpc and internet_gateway:
        print_action(f'Detaching internet gateway: {internet_gateway["InternetGatewayId"]}')
        client = get_ec2_client()
        client.detach_internet_gateway(
            VpcId=vpc['VpcId'],
            InternetGatewayId=internet_gateway['InternetGatewayId']
        )


def delete_internet_gateway(internet_gateway):
    if internet_gateway:
        print_action(f'Deleting internet gateway: {internet_gateway["InternetGatewayId"]}')
        client = get_ec2_client()
        client.delete_internet_gateway(
            InternetGatewayId=internet_gateway['InternetGatewayId']
        )


def delete_vpc(vpc):
    if vpc:
        client = get_ec2_client()
        deleted = False
        retries = 0
        print_action(f'Deleting VPC: {vpc["VpcId"]}')

        while not deleted or retries > 10:
            try:
                client.delete_vpc(
                    VpcId=vpc['VpcId'],
                )
                deleted = True
            except ClientError as error:
                if error.response['Error']['Code'] != 'DependencyViolation':
                    raise error
            retries += 1
            time.sleep(10)


def remove_vpn_gateway_tags(vpn_gateway):
    if vpn_gateway:
        print_action(f'Removing vpn gateway tags from: {vpn_gateway["VpnGatewayId"]}')
        delete_ec2_tags(vpn_gateway['VpnGatewayId'], ['transitVPC1:preferred-path', 'transitVPC1:spoke'])


def detach_vpn_gateway_and_wait_until_detached(vpn_gateway, vpc):
    if vpn_gateway:
        print_action('Waiting for vpn gateway to detach from vpc.')
        detach_vpn_gateway(vpn_gateway, vpc)
        time.sleep(20)

        while get_vpn_gateway_attachment_status(vpc) != 'detached':
            print('.', end='', flush=True)
            time.sleep(20)

        print(' detached\n')


def detach_vpn_gateway(vpn_gateway, vpc):
    client = get_ec2_client()
    try:
        client.detach_vpn_gateway(
            VpcId=vpc['VpcId'],
            VpnGatewayId=vpn_gateway['VpnGatewayId']
        )
    except ClientError as error:
        if error.response['Error']['Code'] != 'InvalidVpnGatewayAttachment.NotFound':
            raise error


def get_vpn_gateway_attach_status(vpn_gateway, vpc):
    client = get_ec2_client()
    response = client.detach_vpn_gateway(
        VpcId=vpc['VpcId'],
        VpnGatewayId=vpn_gateway['VpnGatewayId']
    )

    attachment = response.get('VpcAttachment', None)
    return attachment['State']


def get_ec2_client():
    return get_client('ec2')


def get_iam_client():
    return get_client('iam')


def get_s3_resource():
    return get_resource('s3')


def get_route53_client():
    return get_client('route53')


def get_sts_client():
    return boto3.client('sts')


def get_client(client_type):
    return boto3.client(
        client_type,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region
    )


def get_resource(resource_type):
    return boto3.resource(
        resource_type,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region
    )
