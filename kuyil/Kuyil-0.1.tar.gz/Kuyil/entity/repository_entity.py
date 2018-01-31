from sqlalchemy import Column, Integer, String, NVARCHAR, UniqueConstraint
from Kuyil.entity.base import Base


class RepositoryEntity(Base):

    __tablename__ = 'repository_client_factory'

    __mapper_args__ = {
        'exclude_properties': ['client']
    }

    id = Column(Integer, primary_key=True)
    config = Column(NVARCHAR)
    name = Column(String(500))
    client = None
    UniqueConstraint('name')

    def init(self):
        # call repository_client_factory client factory and get client
        self.client = ""

    def __repr__(self):
        return "<Repository(name='%s', config='%s')>" % (self.name, self.config)
