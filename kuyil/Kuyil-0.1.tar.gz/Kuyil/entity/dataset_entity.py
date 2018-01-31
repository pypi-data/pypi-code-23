from sqlalchemy import Column, Integer, String, BigInteger, Boolean, NVARCHAR, \
    DateTime, UniqueConstraint, VARCHAR
from Kuyil.entity.base import Base
from sqlalchemy.orm import relationship


class DatasetEntity(Base):

    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    dataset_class = Column(String(500))
    instance = Column(String(500))
    label = Column(String(100))
    version = Column(BigInteger)
    tags = Column(String(500), nullable=True)
    alt_uri = Column(VARCHAR, nullable=True)
    read_lock_ts = Column(DateTime, nullable=True)
    write_lock_id = Column(BigInteger, nullable=True)
    write_lock_ts = Column(DateTime, nullable=True)
    is_expired = Column(Boolean, nullable=True)
    is_valid = Column(Boolean)
    is_incomplete = Column(Boolean)
    is_marked_for_deletion = Column(Boolean, nullable=True)
    is_deleted = Column(Boolean, nullable=True)
    created_ts = Column(DateTime)
    modified_ts = Column(DateTime, nullable=True)
    dataset_created_ts = Column(DateTime)
    dataset_ready_ts = Column(DateTime, nullable=True)
    dataset_modified_ts = Column(DateTime, nullable=True)
    dataset_marked_for_deletion_ts = Column(DateTime, nullable=True)
    dataset_deleted_ts = Column(DateTime, nullable=True)
    dataset_expired_ts = Column(DateTime, nullable=True)
    dataset_restored_ts = Column(DateTime, nullable=True)
    comment = Column(NVARCHAR, nullable=True)
    metadata = Column(NVARCHAR, nullable=True)
    bytes = Column(BigInteger, nullable=True)
    lines = Column(Integer, nullable=True)

    repositories = relationship(
        'repository_client_factory',
        secondary='datatset_repository'
    )

    UniqueConstraint('dataset_class', 'instance', 'label', '__version')

    def __repr__(self):
        return "<Dataset(class='%s', instance='%s', label='%s', id='%s')>" % \
               (self.dataset_class, self.instance, self.label, self.id)