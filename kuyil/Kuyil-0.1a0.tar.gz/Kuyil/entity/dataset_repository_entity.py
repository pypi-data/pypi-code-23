from sqlalchemy import Column, Integer, ForeignKey
from Kuyil.entity.base import Base


class DatasetRepositoryEntity(Base):
    __tablename__ = 'datatset_repository'

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer, ForeignKey("repository_client_factory.id"), primary_key=True)
    dataset_id = Column(Integer, ForeignKey("dataset.id"), primary_key=True)

    def __repr__(self):
        return "<DatasetRepository(repository_id='%s', dataset_id='%s')>" % \
               (self.repository_id, self.dataset_id)