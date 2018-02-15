import boto3


def get_repository_client(repository):
    if "s3" in repository.name:
        config = repository.config

        session = boto3.session.Session()

        s3_client = session.client(
            service_name='s3',
            aws_access_key_id=config.get('aws_access_key', ""),
            aws_secret_access_key=config.get('aws_secret_access_key', ""),
        )

        return s3_client

    else:
        None


