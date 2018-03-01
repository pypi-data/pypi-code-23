import yaml

from concreate.descriptor import Descriptor


packages_schema = [yaml.safe_load("""
map:
  name: {type: str}
  state: {type: str}
""")]


class Repository(Descriptor):
    """Object representing package repository

    Args:
      descriptor - yaml representation of repository definition
    """

    def __init__(self, descriptor):
        self.schemas = packages_schema
        super(Repository, self).__init__(descriptor)


    def fetch(self, location): 
       pass
