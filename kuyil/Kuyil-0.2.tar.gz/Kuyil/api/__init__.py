
import json

from Kuyil.api.dataset import Dataset
from Kuyil.api.repository import Repository
from Kuyil.database import database_init
from Kuyil.database import session_factory
from Kuyil.models.repository_entity import RepositoryEntity
import logging
from Kuyil.models.dataset_entity import DatasetEntity


logger = logging.getLogger(__name__)


def get_repository(name):
    session = session_factory()
    repo = session.query(RepositoryEntity). \
        filter(RepositoryEntity.name == name).first()

    logger.info("Name of the repo : " + repo.name)
    return __convert_entity_to_repository(repo)


def create_dataset(dataset_class, instance, label, repository, comment=None,
                   meta_data=None, only_create=False):
    dataset = Dataset(dataset_class, instance, label, repository, comment, meta_data)
    entity = __get_dataset_latest_active_version(dataset)

    if only_create:
        if entity:
            logger.info("Latest active version is idle. Return None")
            return None

        else:
            logger.info("Latest active version is not available. Returning new Dataset")
            return dataset

    else:
        # if active version is present then return it else return the new Dataset created above
        if entity:
            logger.info("Latest active version is idle. Return latest active version")
            return __convert_entity_to_dataset(entity)
        else:
            logger.info("Latest active version is not available. Return new Dataset")
            return dataset


def get_datasets(dataset_class, instance_regex, repository, label=None, all_versions=False):
    pass


def replace_dataset_in_label(dataset_class, instance, source_label, target_label,
                             sink_label, keep_taget_modified_ts=True):
    pass


def init(file_path='config.json'):
    logger.debug("config file path : " + file_path)
    with open(file_path) as json_data_file:
        data = json.load(json_data_file)
    logger.debug(data)
    # Initializing the DB connection.
    database_init(data)


def __get_dataset_latest_active_version(dataset):
    session = session_factory()
    entity = session.query(DatasetEntity). \
        filter(DatasetEntity.label == dataset.label). \
        filter(DatasetEntity.dataset_class == dataset.dataset_class). \
        filter(DatasetEntity.instance == dataset.instance). \
        filter(DatasetEntity.repository == dataset.repository). \
        filter(DatasetEntity.is_incomplete.is_(False)). \
        filter(DatasetEntity.is_valid.is_(True)).order_by(DatasetEntity.version.desc()).first()

    if entity:
        return entity
    else:
        logger.info("No active version exists.")
        return None


def __convert_entity_to_dataset(dataset_entity):
    dataset = Dataset(dataset_entity.dataset_class, dataset_entity.instance, dataset_entity.label,
                      dataset_entity.repository, dataset_entity.comment, dataset_entity.meta_data)
    dataset.id = dataset_entity.id
    return dataset


def __convert_entity_to_repository(repositoryEntity):
    return Repository(repositoryEntity.name, repositoryEntity.config)
