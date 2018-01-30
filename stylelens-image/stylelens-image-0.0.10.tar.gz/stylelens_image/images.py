from bson.objectid import ObjectId
from stylelens_image.database import DataBase

class Images(DataBase):
  def __init__(self):
    super().__init__()
    self.images = self.db.images

  def add_image(self, image):
    try:
      query = {"host_code": image['host_code'],
               "product_no": image['product_no'],
               "version_id": image['version_id']}
      r = self.images.update_one(query,
                                 {"$set":image},
                                 upsert=True)
    except Exception as e:
      print(e)

    return r.raw_result

  def get_image(self, image_id, version_id=None, offset=0, limit=50):
    query = {}
    query['_id'] = ObjectId(image_id)
    if version_id is not None:
      query["version_id"] = version_id

    try:
      r = self.images.find_one(query)
    except Exception as e:
      print(e)

    return r

  def get_images_by_ids(self, ids,
                         version_id=None,
                         offset=0, limit=10):
    query = {}
    _ids = []
    for id in ids:
      _ids.append(ObjectId(id))

    query['_id'] = {'$in': _ids}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def get_images(self, version_id=None, offset=0, limit=50):
    query = {}
    if version_id is None:
      query = {}
    else:
      query = {"version_id": version_id}

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def update_image(self, image):
    query = {}

    query['_id'] = image['_id']
    try:
      r = self.images.update_one(query,
                                 {"$set":image},
                                 upsert=False)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_images(self, version_id, except_version=True):
    query = {}
    if except_version is True:
      query = {"version_id": {"$ne": version_id}}
    else:
      query = {"version_id": version_id}

    try:
      r = self.images.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_all(self):
    query = {}
    try:
      r = self.images.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result
