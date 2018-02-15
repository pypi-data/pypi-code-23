from sqlalchemy import Column, Integer, String, BigInteger, Boolean, NVARCHAR, \
    DateTime, UniqueConstraint, VARCHAR
from sqlalchemy.sql import func

from Kuyil.models.base import Base


class DatasetEntity(Base):

    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    dataset_class = Column(String(500))
    instance = Column(String(500))
    label = Column(String(100))
    version = Column(BigInteger, nullable=False)
    created_ts = Column(DateTime, nullable=False, server_default=func.now())
    repository = Column(String(100), nullable=False)
    tags = Column(String(500), nullable=True)
    alt_uri = Column(VARCHAR(200), nullable=True)
    read_lock_ts = Column(BigInteger, nullable=True)
    write_lock_id = Column(String(100), nullable=True)
    write_lock_ts = Column(BigInteger, nullable=True)
    is_expired = Column(Boolean, nullable=True, default=False)
    is_valid = Column(Boolean, default=False)
    is_incomplete = Column(Boolean, default=True)
    is_marked_for_deletion = Column(Boolean, nullable=True, default=False)
    is_deleted = Column(Boolean, nullable=True, default=False)
    modified_ts = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    dataset_created_ts = Column(BigInteger, nullable=True)
    dataset_ready_ts = Column(BigInteger, nullable=True)
    dataset_modified_ts = Column(BigInteger, nullable=True)
    dataset_marked_for_deletion_ts = Column(DateTime, nullable=True)
    dataset_deleted_ts = Column(DateTime, nullable=True)
    dataset_expired_ts = Column(DateTime, nullable=True)
    dataset_restored_ts = Column(DateTime, nullable=True)
    comment = Column(NVARCHAR(200), nullable=True)
    meta_data = Column(NVARCHAR(200), nullable=True)
    bytes = Column(BigInteger, nullable=True)
    lines = Column(Integer, nullable=True)

    UniqueConstraint('dataset_class', 'instance', 'label', 'version', 'repository')

    UniqueConstraint('dataset_class', 'instance', 'label', 'repository', 'write_lock_id')

    def __repr__(self):
        return "<Dataset(class='%s', instance='%s', label='%s', id='%s', is_incomplete='%s', is_valid='%s')>" % \
               (self.dataset_class, self.instance, self.label, self.id, self.is_incomplete, self.is_valid)

    # include comment, meta_data.
    def __init__(self, Class, instance, label, repository, dataset_created_ts,
                 dataset_modified_ts, comment=None, meta_data=None, version=None):
        self.dataset_class = Class
        self.instance = instance
        self.label = label
        self.repository = repository
        self.dataset_modified_ts = dataset_modified_ts
        self.dataset_created_ts = dataset_created_ts
        self.comment = comment
        self.meta_data = meta_data

        self.version = version
        self.is_valid = False
        self.is_incomplete = True

