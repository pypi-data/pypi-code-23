from bson.objectid import ObjectId
from stylelens_product.database import DataBase

class Versions(DataBase):
  def __init__(self):
    super(Versions, self).__init__()
    self.versions = self.db.versions

  def add_version(self, version):
    try:
      id = self.versions.insert_one(version).inserted_id
    except Exception as e:
      print(e)
      return None

    return str(id)

