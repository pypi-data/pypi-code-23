from bson.objectid import ObjectId
from stylelens_index.database_image import DataBaseImage

class IndexImages(DataBaseImage):
  def __init__(self):
    super().__init__()
    self.images = self.db.images

  def add_image(self, image):
    id = None
    try:
      query = {"host_code": image['host_code'],
               "product_no": image['product_no'],
               "version_id": image['version_id']}
      r = self.images.update_one(query,
                                 {"$set":image},
                                 upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def add_user_image(self, image):
    id = None
    try:
      r = self.images.insert_one(image)
    except Exception as e:
      print(e)
      return None

    return str(r.inserted_id)

  def get_image(self, image_id):
    query = {}
    query['_id'] = ObjectId(image_id)

    try:
      r = self.images.find_one(query)
    except Exception as e:
      print(e)
      return None

    return r

  def get_sim_images(self, image_id):
    query = {}
    query['_id'] = ObjectId(image_id)

    try:
      r = self.images.find_one(query, {'images':1, '_id':0})
    except Exception as e:
      print(e)
      return None

    return r.get('images')

  def get_images(self, version_id,
                  offset=0, limit=10):
    query = {}
    query['version_id'] = version_id

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def delete_all(self):
    query = {}
    try:
      r = self.images.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result
