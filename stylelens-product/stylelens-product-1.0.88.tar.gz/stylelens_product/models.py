from bson.objectid import ObjectId
from stylelens_product.database import DataBase

STATUS_TODO = 'todo'
STATUS_DOING = 'doing'
STATUS_DONE = 'done'


class Models(DataBase):
  def __init__(self):
    super(Models, self).__init__()
    self.models = self.db.models

  def add_model(self, type, version_id):
    model = {}
    model['status'] = STATUS_TODO
    model['type'] = type
    model['path'] = None

    query = {}
    query['type'] = type
    query['version_id'] = version_id
    try:
      r = self.models.update_one(query,
                                 {"$set": model},
                                 upsert=True)
    except Exception as e:
      print(e)

    model_id = None
    if 'upserted' in r.raw_result:
      model_id = str(r.raw_result['upserted'])

    return model_id

  def get_model(self, type, version_id):
    query = {}
    query['type'] = type
    query['version_id'] = version_id
    try:
      r = self.models.find_one(query)
    except Exception as e:
      print(e)

    return r

  def update_model(self, type, version_id, model):
    query = {}
    query['version_id'] = version_id
    query['type'] = type
    try:
      r = self.models.update_one(query, {"$set": model})
    except Exception as e:
      print(e)

    return r.modified_count
