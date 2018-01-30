from stylelens_index.database_object import DataBaseObject

class IndexObjects(DataBaseObject):
  def __init__(self):
    super().__init__()
    self.objects = self.db.objects

  def add_object(self, object):
    id = None
    try:
      query = {"name": object['name'],
               "version_id": object['version_id']}
      r = self.objects.update_one(query,
                                  {"$set":object},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def add_user_object(self, object):
    id = None
    try:
      r = self.objects.insert_one(object)
    except Exception as e:
      print(e)
      return None

    return str(r.inserted_id)

  def get_objects(self, version_id,
                  sort_key=None,
                  sort_order=None,
                  offset=0, limit=10):
    query = {}
    query['version_id'] = version_id

    try:
      if sort_key is None:
        r = self.objects.find(query).skip(offset).limit(limit)
      else:
        r = self.objects.find(query).sort(sort_key, sort_order).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def delete_all(self):
    query = {}
    try:
      r = self.objects.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result
