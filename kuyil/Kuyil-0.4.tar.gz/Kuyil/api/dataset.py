import logging

from Kuyil.api.repository import Repository
from Kuyil.database import session_factory
from Kuyil.models.dataset_entity import DatasetEntity
from Kuyil.models.repository_entity import RepositoryEntity
from Kuyil.utils.date_time_util import Util


class Dataset:

    def __init__(self, dataset_class, instance, label, repository, comment=None,
                 meta_data=None, dataset_created_ts=Util.current_time_millis(),
                 dataset_modified_ts=Util.current_time_millis()
                 ):
        self.instance = instance
        self.dataset_class = dataset_class
        self.label = label
        self.repository = repository
        self.comment = comment
        self.meta_data = meta_data
        self.dataset_created_ts = dataset_created_ts
        self.dataset_modified_ts = dataset_modified_ts
        self.id = None
        self.logger = logging.getLogger(__name__)

    def get_write_lock_if_read_or_idle(self, pid):
        pass

    def get_write_lock_if_idle(self, pid):
        pass

    def get_write_lock_if_write_read_or_idle(self, pid):

        """
        check if there is no active or inactive version with same pid
        if so:
            return None
        else:
            create a new version.
            Persist it in mysql table.
            Mutate internal field - id
            Query repository_entity from repository table using repository_name
            Take the write lock by incrementing write_lock_ts
            Persist
            return write_lock_ts
        """

        if self.__get_dataset_count_with_pid(pid):
            self.logger.info("Dataset with this pid already exists. Returning None")
            return None

        dataset_entity = self.__convert_dataset_to_entity(self)
        dataset_entity = self.__persist_dataset(dataset_entity)
        id = dataset_entity.id
        if id:
            self.logger.debug("This is the id of the new dataset : " + str(dataset_entity.id))
            self.id = id
            self.logger.debug("Get write lock on Dataset and update it")
            dataset_entity.write_lock_id = pid
            dataset_entity.write_lock_ts = Util.lock_time_millis()
            dataset_entity.is_incomplete = True
            dataset_entity.is_valid = False
            self.__persist_dataset(dataset_entity)
            return dataset_entity.write_lock_ts
        else:
            self.logger.warn("An error occurred while persisting dataset")
            return None

    def __get_dataset_count_with_pid(self, pid):
        session = session_factory()
        return session.query(DatasetEntity). \
            filter(DatasetEntity.label == self.label). \
            filter(DatasetEntity.dataset_class == self.dataset_class). \
            filter(DatasetEntity.instance == self.instance). \
            filter(DatasetEntity.repository == self.repository). \
            filter(DatasetEntity.write_lock_id == pid).count()

    def maintain_write_lock(self, pid):

        """
        Mantain the write lock by incrementing the write_lock_ts value by 5 mins
        :param pid:
        :return: updated write_lock_ts

        k = Query for the dataset qualifier dataset_class, instance, label, pid
        if k:
            update the write_lock_ts to current_time + 5 mins
        else :
            :exception
        """
        entity = self.__get_dataset_with_pid(self, pid)
        current_time = Util.current_time_millis()
        if entity and entity.write_lock_ts >= current_time:
            entity.write_lock_ts = Util.lock_time_millis()
            entity.dataset_modified_ts = current_time
            self.__persist_dataset(entity)
            return entity.write_lock_ts
        else:
            self.logger.info("Cannot obtain write lock as it expired or does not exist.")
            return None

    def write_failed(self, pid, comment=None):

        """
        :param pid:
        :param comment:
        :return: True/False on basis of success or failure

         k = Query for the dataset qualifier dataset_class, instance, label, pid
         if k:
            release write lock by updating write_lock_ts to current_timestamp
            update the comment
         else :
            :exception

        """
        entity = self.__get_dataset_with_pid(self, pid)
        if entity and entity.write_lock_ts >= Util.current_time_millis():
            current_time = Util.current_time_millis()
            entity.write_lock_ts = current_time
            entity.comment = comment
            entity.write_lock_id = None
            entity.dataset_modified_ts = current_time
            self.__persist_dataset(entity)
            return True
        else:
            return False

    def write_success(self, pid, comment=None):

        """
        :param pid:
        :param comment:
        :return: True/False on basis of success or failure

                 k = Query for the dataset qualifier dataset_class, instance, label, pid
                 if k:
                    release write lock by updating write_lock_ts to current_timestamp
                    update is_incomplete to false
                    update is_valid to true
                    update pid to None  so as to resolve conflict
                    update the comment
                 else :
                    :exception
        """

        entity = self.__get_dataset_with_pid(self, pid)

        if entity and entity.write_lock_ts >= Util.current_time_millis():
            entity.is_incomplete = False
            entity.is_valid = True
            entity.write_lock_id = None
            current_time = Util.current_time_millis()
            entity.write_lock_ts = current_time
            entity.dataset_ready_ts = current_time
            entity.dataset_modified_ts = current_time
            entity.comment = comment
            self.__persist_dataset(entity)
            return True
        else:
            return False

    def __get_latest_active_version(self):

        session = session_factory()
        entity = session.query(DatasetEntity). \
            filter(DatasetEntity.label == self.label). \
            filter(DatasetEntity.dataset_class == self.dataset_class). \
            filter(DatasetEntity.instance == self.instance). \
            filter(DatasetEntity.repository == self.repository). \
            filter(DatasetEntity.is_incomplete.is_(False)). \
            filter(DatasetEntity.is_valid.is_(True)).order_by(DatasetEntity.version.desc()).first()

        if entity:
            return entity
        else:
            self.logger.warn("No active version exists")
            return None

    def __get_latest_version(self):
        session = session_factory()
        entity = session.query(DatasetEntity). \
            filter(DatasetEntity.label == self.label). \
            filter(DatasetEntity.dataset_class == self.dataset_class). \
            filter(DatasetEntity.instance == self.instance). \
            filter(DatasetEntity.repository == self.repository). \
            order_by(DatasetEntity.version.desc()).first()

        if entity:
            return entity
        else:
            self.logger.warn("Can not find any latest version.")
            return None

    def __get_dataset_with_pid(self, dataset, pid=None):
        session = session_factory()
        self.logger.debug("Inside get_dataset_with_pid")
        if not pid:
            entity = session.query(DatasetEntity). \
                filter(DatasetEntity.label == self.label). \
                filter(DatasetEntity.dataset_class == self.dataset_class). \
                filter(DatasetEntity.instance == self.instance). \
                filter(DatasetEntity.repository == self.repository). \
                filter(DatasetEntity.id == dataset.id).first()
            self.logger.debug(entity)
            return entity
        else:
            entity = session.query(DatasetEntity). \
                filter(DatasetEntity.label == self.label). \
                filter(DatasetEntity.dataset_class == self.dataset_class). \
                filter(DatasetEntity.instance == self.instance). \
                filter(DatasetEntity.repository == self.repository). \
                filter(DatasetEntity.write_lock_id == pid).first()
            self.logger.debug(entity)
            return entity

    def __get_dataset(self, dataset_entity):
        session = session_factory()
        entity = session.query(DatasetEntity). \
            filter(DatasetEntity.label == dataset_entity.label). \
            filter(DatasetEntity.dataset_class == dataset_entity.dataset_class). \
            filter(DatasetEntity.instance == dataset_entity.instance). \
            filter(DatasetEntity.repository == self.repository). \
            filter(DatasetEntity.version == dataset_entity.version).first()

        if entity:
            return entity
        else:
            return None

    def __get_repository(self, name):
        session = session_factory()
        repo = session.query(RepositoryEntity). \
            filter(RepositoryEntity.name == name).first()

        self.logger.info("Name of the repo : " + repo.name)
        return Repository.__convert_entity_to_repository(repo)

    def __persist_dataset(self, dataset_entity):
        session = session_factory()
        session.add(dataset_entity)
        self.logger.debug("Persist this entity : ")
        self.logger.debug(dataset_entity)
        session.commit()
        return self.__get_dataset(dataset_entity)

    # need to fix this for multiple concurrent clients.
    # as of now mysql contraint won't allow same version through multiple clients
    def __convert_dataset_to_entity(self, dataset):
        entity = self.__get_latest_version()
        version = 1
        if entity:
            version += entity.version

        return DatasetEntity(dataset.dataset_class, dataset.instance, dataset.label, dataset.repository,
                             dataset.dataset_created_ts, dataset.dataset_modified_ts, dataset.comment, dataset.meta_data, version)

    def __convert_entity_to_dataset(self, dataset_entity):
        dataset = Dataset(dataset_entity.dataset_class, dataset_entity.instance, dataset_entity.label,
                          dataset_entity.repository, dataset_entity.comment, dataset_entity.meta_data)
        dataset.id = dataset_entity.id
        return dataset

    def get_read_lock(self):

        entity = self.__get_latest_active_version()
        if entity:
            self.id = entity.id
            entity.read_lock_ts = Util.lock_time_millis()
            self.__persist_dataset(entity)
            return True
        else:
            return False

    def mantain_read_lock(self):
        """
        Query dataset by Id rather than getting latest active version.
        :return:
        """
        entity = self.__get_dataset_with_pid(self)
        if entity:
            entity.read_lock_ts = Util.lock_time_millis()
            self.__persist_dataset(entity)
            return True
        else:
            return False

    def is_write_locked(self):
        entity = self.__get_dataset_with_pid(self)
        if not entity:
            return True
        if entity.write_lock_ts > Util.current_time_millis():
            return True
        else:
            return False

    def is_read_locked(self):
        entity = self.__get_dataset_with_pid(self)
        if not entity:
            return True
        if entity.read_lock_ts > Util.current_time_millis():
            return True
        else:
            return False

    def get_resource_uri(self):
        repository = self.__get_repository(self.repository)
        repository.get_resource_uri(self.dataset_class, self.instance, self.id)

    def set_validity(self, validity):
        """
        :param validity:
        :return:

        Query by Id and set validity
        """

        pass

    def set_deleted(self, is_deleted):
        """

        :param is_deleted:
        :return:

        Query by id and set is_deleted
        """
        pass

    def read_finished(self, pid, comment=None):
        """

        :param pid:
        :param comment:
        :return:

        Query by id and set read_lock_ts to current time.
        """
        entity = self.__get_dataset_with_pid(self)
        if entity and entity.read_lock_ts >= Util.current_time_millis():
            entity.read_lock_ts = Util.current_time_millis()
            self.__persist_dataset(entity)
            return True
        else:
            return False

    def get_metadata(self):
        return self.meta_data

    def set_metadata(self, **kwargs):

        pass

    def set_metadata_key_value(self, key, value):

        pass

    def get_class(self):
        return self.dataset_class

    def get_instance(self):
        return self.instance

    def get_label(self):
        return self.label
