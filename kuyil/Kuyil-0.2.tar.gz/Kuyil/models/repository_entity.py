from sqlalchemy import Column, Integer, String, NVARCHAR, UniqueConstraint
from Kuyil.models.base import Base


class RepositoryEntity(Base):

    __tablename__ = 'repository'

    __mapper_args__ = {
        'exclude_properties': ['client']
    }

    id = Column(Integer, primary_key=True)
    config = Column(NVARCHAR(1000))
    name = Column(String(500))
    client = None
    UniqueConstraint('name')

    def init(self):
        # call repository_client client factory and get client
        self.client = ""

    def __repr__(self):
        return "<Repository(name='%s', config='%s')>" % (self.name, self.config)

    def __init__(self, name, config):
        self.name = name
        self.config = config
