from configparser import ConfigParser
import json
import os
import ibm_boto3
from ibm_botocore.client import Config
import wget
import uuid


if "ENV" in os.environ:
    environment = os.environ['ENV']
else:
    environment = "SVT"


config = ConfigParser()
config.read('../config.ini')


def get_env():
    return environment


def get_wml_credentials():
    return json.loads(config.get(environment, 'wml_credentials'))


def get_cos_credentials():
    return json.loads(config.get(environment, 'cos_credentials'))


def get_cos_auth_endpoint():
    return config.get(environment, 'cos_auth_endpoint')


def get_cos_service_endpoint():
    return config.get(environment, 'cos_service_endpoint')


def get_client():
    wml_lib = __import__('watson_machine_learning_client', globals(), locals())
    return wml_lib.WatsonMachineLearningAPIClient(get_wml_credentials())


def get_cos_resource():
    cos_credentials = get_cos_credentials()
    api_key = cos_credentials['apikey']
    service_instance_id = cos_credentials['resource_instance_id']
    auth_endpoint = get_cos_auth_endpoint()
    service_endpoint = get_cos_service_endpoint()

    cos = ibm_boto3.resource(
        's3',
        ibm_api_key_id = api_key,
        ibm_service_instance_id = service_instance_id,
        ibm_auth_endpoint = auth_endpoint,
        config = Config(signature_version='oauth'),
        endpoint_url = service_endpoint
    )

    return cos


def prepare_cos(cos_resource, bucket_prefix='wml-test'):
    # Use with caution
    # ================
    # client = get_client()
    # clean_env(client, cos_resource)

    postfix = str(uuid.uuid4())

    bucket_names = {
        'data': bucket_prefix + '-' + postfix,
        'results': bucket_prefix + '-results-' + postfix
    }

    cos_resource.create_bucket(Bucket=bucket_names['data'])
    upload_data(cos_resource, bucket_names['data'])

    cos_resource.create_bucket(Bucket=bucket_names['results'])

    return bucket_names


def upload_data(cos_resource, bucket_name):
    data_links = [
        'http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz',
        'http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz'
    ]

    data_dir = 'MNIST_DATA'

    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    for link in data_links:
        if not os.path.isfile(os.path.join(data_dir, os.path.join(link.split('/')[-1]))):
            wget.download(link, out=data_dir)

    bucket_obj = cos_resource.Bucket(bucket_name)

    for filename in os.listdir(data_dir):
        with open(os.path.join(data_dir, filename), 'rb') as data:
            bucket_obj.upload_file(os.path.join(data_dir, filename), filename)
            print('{} is uploaded.'.format(filename))

    for obj in bucket_obj.objects.all():
        print('Object key: {}'.format(obj.key))
        print('Object size (kb): {}'.format(obj.size/1024))


def download_data(cos_resource):
    pass


def get_cos_training_data_reference(bucket_names):
    cos_credentials = get_cos_credentials()
    service_endpoint = get_cos_service_endpoint()

    return {
        "connection": {
            "endpoint_url": service_endpoint,
            "access_key_id": cos_credentials['cos_hmac_keys']['access_key_id'],
            "secret_access_key": cos_credentials['cos_hmac_keys']['secret_access_key']
        },
        "source": {
            "bucket": bucket_names['data'],
        },
        "type": "s3"
    }


def get_cos_training_results_reference(bucket_names):
    cos_credentials = get_cos_credentials()
    service_endpoint = get_cos_service_endpoint()

    return {
        "connection": {
            "endpoint_url": service_endpoint,
            "access_key_id": cos_credentials['cos_hmac_keys']['access_key_id'],
            "secret_access_key": cos_credentials['cos_hmac_keys']['secret_access_key']
        },
        "target": {
            "bucket": bucket_names['results'],
        },
        "type": "s3"
    }

def clean_cos_bucket(cos_resource, bucket_name):
    bucket_obj = cos_resource.Bucket(bucket_name)
    for o in bucket_obj.objects.all():
        o.delete()
    bucket_obj.delete()


def clean_cos(cos_resource, bucket_names):
    clean_cos_bucket(cos_resource, bucket_names['data'])
    clean_cos_bucket(cos_resource, bucket_names['results'])


def clean_env(client, cos_resource):
    clean_experiments(client)
    clean_definitions(client)
    clean_models(client)

    for bucket in cos_resource.buckets.all():
        if 'wml-test-' in bucket.name:
            print('Deleting \'{}\' bucket.'.format(bucket.name))
            bucket_obj = cos_resource.Bucket(bucket.name)
            for o in bucket_obj.objects.all():
                o.delete()
            bucket.delete()


def clean_models(client):
    details = client.repository.get_model_details()

    for model_details in details['resources']:
        print('Deleting \'{}\' model.'.format(model_details['metadata']['guid']))
        client.repository.delete(model_details['metadata']['guid'])


def clean_definitions(client):
    details = client.repository.get_definition_details()

    for definition_details in details['resources']:
        print('Deleting \'{}\' definition.'.format(definition_details['metadata']['guid']))
        client.repository.delete(definition_details['metadata']['guid'])


def clean_experiments(client):
    details = client.repository.get_experiment_details()

    for experiment_details in details['resources']:
        print('Deleting \'{}\' experiment.'.format(experiment_details['metadata']['guid']))
        client.repository.delete(experiment_details['metadata']['guid'])