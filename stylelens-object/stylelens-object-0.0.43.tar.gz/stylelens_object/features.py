
from bson.objectid import ObjectId
from stylelens_object.database_feature import DataBaseFeature

class Features(DataBaseFeature):
  def __init__(self):
    super(Features, self).__init__()
    self.features = self.db.features

  def add_feature(self, feature):
    query = {}

    query['object_id'] = feature['object_id']

    try:
      r = self.features.update_one(query,
                                  {"$set": feature},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])
      return id
    else:
      return None

  def get_feature_by_object_id(self, object_id):
    query = {}

    query['object_id'] = object_id

    try:
      r = self.features.find_one(query)
    except Exception as e:
      print(e)

    return r

  def get_features(self, version_id=None, offset=0, limit=50):
    query = {}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.features.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_size_features(self):
    query = {}

    try:
      count = self.features.find(query).count()
    except Exception as e:
      print(e)

    return count

  def delete_all(self):
    query = {}
    try:
      r = self.features.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result
