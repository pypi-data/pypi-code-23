import json
import logging

from Kuyil.models.repository_entity import RepositoryEntity
from Kuyil.repository_client.repository_client_helper import get_repository_client


class Repository:

    def __init__(self, name, config):
        self.name = name
        self.config = json.loads(config)
        self.client = get_repository_client(self)
        self.logger = logging.getLogger(__name__)

    def init(self):
        self.client = get_repository_client(self)

    # avoiding **kwargs in the arguments
    def create_uri(self, dataset_class, instance, id, overwrite=False):
        bucket = self.config.get("bucket", "Kuyil")
        prefix = self.config.get("prefix", "test") + "/" + str(dataset_class) + "/" \
                        + str(instance) + "/" + str(id) + "/"

        try:
            self.client.put_object(
                Bucket=bucket,
                Body='',
                Key=prefix
            )
            return "s3://" + bucket + "/" + prefix
        except Exception:
            return None


    def get_resource_uri(self, dataset_class, instance, id):
        """

        :param dataset_class:
        :param instance:
        :param id:
        :return: URL/None

        create URL from class, instance, id
        call does_uri_exists()
        if yes:
            return uri
        else:
            return None
        """
        bucket = self.config.get("bucket", "Kuyil")
        prefix = self.config.get("prefix", "test") + "/" + str(dataset_class) + "/" \
                 + str(instance) + "/" + str(id) + "/"

        uri = "s3://" + bucket + "/" + prefix
        return uri

    def does_uri_exists(self, dataset_class, instance, id):

        bucket = self.config.get("bucket", "Kuyil")
        prefix = self.config.get("prefix", "test") + "/" + str(dataset_class) + "/" \
                 + str(instance) + "/" + str(id) + "/"

        client = self.client
        response = client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
        )
        for obj in response.get('Contents', []):
            if prefix in obj['Key']:
                return True
        return False

    def delete_uri(self, dataset_class, instance, id):

        bucket = self.config.get("bucket", "Kuyil")
        prefix = self.config.get("prefix", "test") + "/" + str(dataset_class) + "/" \
                 + str(instance) + "/" + str(id) + "/"
        self.client.delete_object(Bucket=bucket, Key=prefix)

    @staticmethod
    def __convert_entity_to_repository(repositoryEntity):
        return Repository(repositoryEntity.name, repositoryEntity.config)

    @staticmethod
    def __convert_repository_to_entity(repository):
        return RepositoryEntity(repository.name, json.dumps(repository.config))