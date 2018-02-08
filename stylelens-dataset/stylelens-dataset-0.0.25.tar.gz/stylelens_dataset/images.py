from bson.objectid import ObjectId
from stylelens_dataset.database import DataBase

class Images(DataBase):
  def __init__(self):
    super(Images, self).__init__()
    self.images = self.db.images

  def get_image(self, id):
    try:
      r = self.images.find_one({"_id": ObjectId(id)})
    except Exception as e:
      print(e)

    return r

  def add_image(self, image):
    image_id = None
    try:
      r = self.images.update_one({"file": image['file']},
                                  {"$set": image},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      image_id = str(r.raw_result['upserted'])

    return image_id

  def get_images_by_source(self, source,  offset=0, limit=50):
    query = {"source":source}

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_images_by_category_class(self, clazz,  offset=0, limit=50):
    query = {"category_class":clazz}

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_images_by_category_name(self, category_name,
                                  is_confirmed=None,
                                  offset=0, limit=50):
    query = {"category_name":category_name}

    if is_confirmed is None:
      query['is_confirmed'] = {'$exists':False}
    else:
      query['is_confirmed'] = is_confirmed

    try:
      r = self.images.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_images_count_by_category_name(self, category_name, is_confirmed=None):
    query = {"category_name":category_name}

    if is_confirmed is None:
      query['is_confirmed'] = {'$exists':False}
    else:
      query['is_confirmed'] = is_confirmed

    try:
      r = self.images.find(query).count()
    except Exception as e:
      print(e)

    return r

  def update_image(self, image):
    try:
      r = self.images.update_one({"_id": image['_id']},
                                  {"$set": image})
    except Exception as e:
      print(e)
      return None

    return r.raw_result

  def validate_images(self, ids, confirmed=True):
    try:
      bulk = self.images.initialize_unordered_bulk_op()
      for i in ids:
        img = {}
        img['is_confirmed'] = confirmed
        bulk.find({'_id': ObjectId(i)}).update({'$set': img})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)

  def update_images(self, images):
    try:
      bulk = self.images.initialize_unordered_bulk_op()
      for i in range(0, len(images)):
        bulk.find({'_id': images[i]['_id']}).update({'$set': images[i]})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)
