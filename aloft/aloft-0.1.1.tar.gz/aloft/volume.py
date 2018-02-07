import copy
from aloft import aws
from aloft import cluster
from aloft import chart_config
from aloft import k8s
from aloft import output
from aloft.process import execute
from tempfile import NamedTemporaryFile


def remove_released_volume_resources(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    cluster_id = release_config['cluster']
    vpc_id = cluster.get_vpc_id_by_cluster_id(cluster_id)

    for chart in charts:
        bucket_name = get_persistent_volumes_bucket_name(vpc_id)
        filename = get_persistent_volumes_filename(chart_set, release_id, chart, sandbox_name)
        output.print_action(f'Removing released volume resources defined in s3://{bucket_name}/{filename}')
        volume_definitions_filename = save_persistent_volume_definitions_from_s3(bucket_name, filename)

        if volume_definitions_filename:
            execute(f'kubectl delete -f {volume_definitions_filename}')
        else:
            output.print_details(f'No volume resources found.')


def restore_volumes(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    cluster_id = release_config['cluster']
    vpc_id = cluster.get_vpc_id_by_cluster_id(cluster_id)

    for chart in charts:
        bucket_name = get_persistent_volumes_bucket_name(vpc_id)
        filename = get_persistent_volumes_filename(chart_set, release_id, chart, sandbox_name)
        output.print_action(f'Restoring persistent volumes from s3://{bucket_name}/{filename}')
        volume_definitions_filename = save_persistent_volume_definitions_from_s3(bucket_name, filename)

        if volume_definitions_filename:
            k8s.apply_file(volume_definitions_filename)
        else:
            output.print_details(f'No volume resources found.')


def save_persistent_volume_definitions_from_s3(bucket_name, filename):
    content = aws.get_content_from_s3(bucket_name, filename)
    created_filename = None

    if content:
        with NamedTemporaryFile(mode='w+t', encoding='utf-8', delete=False) as temp_file:
            temp_file.write(content)
            temp_file.write('\n')
            created_filename = temp_file.name

    return created_filename


def unlock_volumes(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']

    for chart in charts:
        persistent_volume_names = get_chart_persistent_volume_names(chart, namespace)

        if persistent_volume_names:
            unlock_volume(release_id, chart_set, sandbox_name, chart, persistent_volume_names)


def unlock_volume(release_id, chart_set, sandbox_name, chart, persistent_volume_names):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    cluster_id = release_config['cluster']
    vpc_id = cluster.get_vpc_id_by_cluster_id(release_config['cluster'])

    output.print_action(f'Unlocking persistent volumes: {persistent_volume_names}')

    for persistent_volume_name in persistent_volume_names:
        release_persistent_volume(cluster_id, persistent_volume_name)

    bucket_name = get_persistent_volumes_bucket_name(vpc_id)
    filename = get_persistent_volumes_filename(chart_set, release_id, chart, sandbox_name)
    delete_persistent_volume_definitions_from_s3(bucket_name, filename)


def release_persistent_volume(cluster_id, persistent_volume_name):
    persistent_volume = get_persistent_volume(persistent_volume_name)
    set_persistent_volume_reclaim_policy(persistent_volume, 'Delete')
    attach_volume_to_kops(persistent_volume, cluster_id)


def lock_volumes(release_id, chart_set, charts, sandbox_name):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    namespace = release_config['namespace']

    for chart in charts:
        persistent_volume_names = get_chart_persistent_volume_names(chart, namespace)

        if persistent_volume_names:
            lock_volume(release_id, chart_set, sandbox_name, chart, persistent_volume_names)


def lock_volume(release_id, chart_set, sandbox_name, chart, persistent_volume_names):
    release_config = chart_config.get_release_config(chart_set, release_id, sandbox_name)
    cluster_id = release_config['cluster']
    vpc_id = cluster.get_vpc_id_by_cluster_id(release_config['cluster'])
    persistent_volumes = []

    output.print_action(f'Locking persistent volumes: {persistent_volume_names}')

    for persistent_volume_name in persistent_volume_names:
        retain_persistent_volume(cluster_id, persistent_volume_name, persistent_volumes)

    bucket_name = get_persistent_volumes_bucket_name(vpc_id)
    filename = get_persistent_volumes_filename(chart_set, release_id, chart, sandbox_name)
    save_persistent_volume_definitions_to_s3(persistent_volumes, bucket_name, filename)


def retain_persistent_volume(cluster_id, persistent_volume_name, persistent_volumes):
    persistent_volume = get_persistent_volume(persistent_volume_name)
    set_persistent_volume_reclaim_policy(persistent_volume, 'Retain')
    release_volume_from_kops(persistent_volume, cluster_id)
    persistent_volumes.append(clean_persistent_volume_definition(persistent_volume))


def get_persistent_volumes_bucket_name(vpc_id):
    return f'persistent-volumes.{vpc_id}'


def get_persistent_volumes_filename(chart_set, release_id, chart, sandbox_name):
    filename = f'{release_id}_{chart_set}_{chart}.yaml'

    if sandbox_name:
        filename = f'{sandbox_name}_{filename}'

    return filename


def set_persistent_volume_reclaim_policy(persistent_volume, reclaim_policy):
    persistent_volume_name = get_persistent_volume_name(persistent_volume)

    output.print_action(f'Setting persistent volume reclaim policy for {persistent_volume_name} to {reclaim_policy}')

    if persistent_volume['spec']['persistentVolumeReclaimPolicy'] != reclaim_policy:
        reclaim_policy_spec = '\'{"spec":{"persistentVolumeReclaimPolicy":"' + reclaim_policy + '"}}\''
        # execute(f'kubectl patch pv {persistent_volume_name} -p {reclaim_policy_spec}')
        persistent_volume['spec']['persistentVolumeReclaimPolicy'] = reclaim_policy


def release_volume_from_kops(persistent_volume, cluster_id):
    persistent_volume_name = get_persistent_volume_name(persistent_volume)
    output.print_action(f'Releasing persistent volume {persistent_volume_name} from Kops.')
    volume_resource_id = get_aws_volume_resource_id(persistent_volume)
    aws.delete_ec2_tags(volume_resource_id, [f'kubernetes.io/cluster/{cluster_id}', 'KubernetesCluster', 'LockedOnCluster'])
    aws.create_ec2_tags(volume_resource_id, {'LockedOnCluster': cluster_id})


def attach_volume_to_kops(persistent_volume, cluster_id):
    persistent_volume_name = get_persistent_volume_name(persistent_volume)
    output.print_action(f'Attaching persistent volume {persistent_volume_name} to Kops.')
    volume_resource_id = get_aws_volume_resource_id(persistent_volume)
    aws.delete_ec2_tags(volume_resource_id, [f'kubernetes.io/cluster/{cluster_id}', 'KubernetesCluster', 'LockedOnCluster'])
    aws.create_ec2_tags(volume_resource_id, {
        f'kubernetes.io/cluster/{cluster_id}': 'owned',
        'KubernetesCluster': cluster_id
    })


def get_aws_volume_resource_id(persistent_volume):
    return persistent_volume['spec']['awsElasticBlockStore']['volumeID'].split('/')[-1]


def get_chart_persistent_volume_names(chart, namespace):
    resource_name = f'{namespace}-{chart}'
    persistent_volume_claims = k8s.get_resources('pvc', namespace, 'release', resource_name)
    persistent_volume_names = []

    for persistent_volume_claim in persistent_volume_claims:
        persistent_volume_name = persistent_volume_claim['spec']['volumeName']
        persistent_volume_names.append(persistent_volume_name)

    return persistent_volume_names


def get_persistent_volume(persistent_volume_name):
    return k8s.get_resource_by_name('pv', persistent_volume_name)


def get_persistent_volume_name(persistent_volume):
    return persistent_volume['metadata']['name']


def clean_persistent_volume_definition(persistent_volume):
    keys_to_keep = ['apiVersion', 'kind', 'metadata', 'spec']
    metadata_keys_to_keep = ['name']
    claim_keys_to_keep = ['apiVersion', 'kind', 'name', 'namespace']

    cleaned_volume = copy.deepcopy(persistent_volume)
    cleaned_volume = {key: cleaned_volume[key] for key in keys_to_keep}
    cleaned_volume['metadata'] = {key: cleaned_volume['metadata'][key] for key in metadata_keys_to_keep}
    cleaned_volume['spec']['claimRef'] = {key: cleaned_volume['spec']['claimRef'][key] for key in claim_keys_to_keep}

    return cleaned_volume


def save_persistent_volume_definitions_to_s3(persistent_volumes, bucket_name, filename):
    output.print_action(f'Saving persistent volume definition to s3://{bucket_name}/{filename}')
    content = output.list_as_yaml_file_data(persistent_volumes)
    output.print_details(content)
    aws.save_content_to_s3(content, bucket_name, filename)


def delete_persistent_volume_definitions_from_s3(bucket_name, filename):
    output.print_action(f'Deleting persistent volume definition from s3://{bucket_name}/{filename}')
    aws.delete_file_in_s3(bucket_name, filename)
