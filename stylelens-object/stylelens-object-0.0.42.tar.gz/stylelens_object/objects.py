
from bson.objectid import ObjectId
from stylelens_object.database import DataBase

class Objects(DataBase):
  def __init__(self):
    super(Objects, self).__init__()
    self.objects = self.db.objects

  def get_object(self, object_id, version_id=None):
    query = {}

    query['_id'] = ObjectId(object_id)
    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.objects.find_one(query)
    except Exception as e:
      print(e)

    return r

  def get_object_by_index(self, index, version_id):
    query = {}

    query['version_id'] = version_id
    query['index'] = index
    try:
      r = self.objects.find_one(query)
    except Exception as e:
      print(e)

    return r

  def get_objects_with_null_index(self, version_id=None, offset=0, limit=50):
    query = {}

    if version_id is None:
      query = {"index":None, "feature": {"$ne":None}, "version_id": {"$ne":None}}
    else:
      query = {"index":None, "feature": {"$ne":None}, "version_id":version_id}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_with_null_feature(self, version_id=None, offset=0, limit=50):
    query = {}

    if version_id is not None:
      query['version_id'] = version_id

    query['feature'] = {'$exists':False}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects(self, version_id,
                  is_indexed=None,
                  image_indexed=None,
                  sort_key=None,
                  sort_order=None,
                  is_main=None,
                  offset=0, limit=10):
    query = {}
    query['version_id'] = version_id

    if is_indexed is False:
      query['$or'] = [{'index':{'$exists':False}}, {'index':None}]
    elif is_indexed is True:
      query['index'] = {"$ne":None}

    if image_indexed is False:
      query['$or'] = [{'image_indexed':{'$exists':False}}, {'image_indexed':False}]
    elif image_indexed is True:
      query['image_indexed'] = True

    if is_main is False:
      query['is_main'] = False
    elif is_main is True:
      query['is_main'] = True

    try:
      if sort_key is None:
        r = self.objects.find(query).skip(offset).limit(limit)
      else:
        r = self.objects.find(query).sort(sort_key, sort_order).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def get_objects_by_ids(self, ids,
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
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def get_objects_by_indexes(self, indexes,
                             version_id=None,
                             offset=0, limit=10):
    query = {}
    query['index'] = {'$in': indexes}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def get_object_ids(self, version_id,
                      is_indexed=None,
                      image_indexed=None,
                      offset=0, limit=10):
    query = {}
    query['version_id'] = version_id

    if is_indexed is False:
      query['$or'] = [{'index':{'$exists':False}}, {'index':None}]
    elif is_indexed is True:
      query['index'] = {"$ne":None}

    if image_indexed is False:
      query['$or'] = [{'image_indexed':{'$exists':False}}, {'image_indexed':False}, {'image_indexed':None}]
    elif image_indexed is True:
      query['image_indexed'] = True

    try:
      r = self.objects.find(query, {'_id':True}).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def get_size_objects(self, version_id, is_indexed=None, image_indexed=None):
    query = {}
    query['version_id'] = version_id

    if is_indexed is True:
      query['index'] = {"$exists":True}
    elif is_indexed is False:
      query['index'] = {"$exists":False}

    if image_indexed is True:
      query['image_indexed'] = True
    elif image_indexed is False:
      query['$or'] = [{'image_indexed':{'$exists':False}}, {'image_indexed':False}]

    try:
      count = self.objects.find(query).count()
    except Exception as e:
      print(e)

    return count

  def add_object(self, object):
    object_id = None
    try:
      r = self.objects.update_one({"name": object['name']},
                                  {"$set": object},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      object_id = str(r.raw_result['upserted'])

    return object_id

  def update_object(self, object):
    try:
      r = self.objects.update_one({"name": object['name']},
                                  {"$set": object})
    except Exception as e:
      print(e)
      return None

    return r.raw_result

  def update_object_by_id(self, id, object):
    try:
      r = self.objects.update_one({"_id": ObjectId(id)},
                                  {"$set": object})
    except Exception as e:
      print(e)
      return None

    return r.raw_result

  def update_objects_by_id(self, objects):
    try:
      bulk = self.objects.initialize_unordered_bulk_op()
      for i in range(0, len(objects)):
        bulk.find({'_id': ObjectId(objects[i]['object_id'])}).update({'$set': objects[i]})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)

  def update_objects_by_name(self, objects):
    try:
      bulk = self.objects.initialize_unordered_bulk_op()
      for i in range(0, len(objects)):
        bulk.find({'name': objects[i]['name']}).update({'$set': objects[i]})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)

  def reset_index(self, version_id=None):
    query = {}
    obj = {"index": None}

    if version_id is None:
      query = {"index":{"$ne":None}, "version_id": {"$ne":None}}
    else:
      query = {"index":{"$ne":None}, "version_id":version_id}
    try:
      r = self.objects.update_many(query, {"$set":obj})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result

  def reset_image_index(self, version_id=None):
    query = {}
    obj = {"image_indexed": None}

    if version_id is None:
      query = {"image_indexed":{"$ne":None}, "version_id": {"$ne":None}}
    else:
      query = {"image_indexed":{"$ne":None}, "version_id":version_id}
    try:
      r = self.objects.update_many(query, {"$set":obj})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result

  def delete_object(self, object_id):
    query = {}
    query['_id'] = ObjectId(object_id)
    try:
      r = self.objects.delete_one(query)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_all(self):
    query = {}
    try:
      r = self.objects.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result
