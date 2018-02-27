from aws_boto3.ecs import utils


def ecs_ensure_config(config, region=None):
    response = {'cluster_arn': utils.ensure_cluster(config['cluster_definition'], region=region)}
    service_response = None
    if 'services' in config:
        services = config['services']
        response['services'] = []
        for service in services:
            service['service_definition']['cluster'] = response['cluster_arn']
            service_response = utils.ensure_service(service, region=region)
            response['services'].append(service_response)
    return response
