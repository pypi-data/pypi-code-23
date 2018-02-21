from bson.objectid import ObjectId
from stylelens_product.database import DataBase

class Versions(DataBase):
  def __init__(self):
    super(Versions, self).__init__()
    self.versions = self.db.versions

  def add_version(self, version):
    id = None
    query = {"host_group": version['host_group']}
    try:
      r = self.versions.update_one(query,
                                  {"$set": version},
                                  upsert=True)
    except Exception as e:
      print(e)
      return None

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

