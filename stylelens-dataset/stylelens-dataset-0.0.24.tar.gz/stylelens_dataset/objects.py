from bson.objectid import ObjectId
from stylelens_dataset.database import DataBase

class Objects(DataBase):
  def __init__(self):
    super(Objects, self).__init__()
    self.objects = self.db.objects

  def get_object(self, object_id):
    try:
      r = self.objects.find_one({"_id": ObjectId(object_id)})
    except Exception as e:
      print(e)

    return r

  def add_object(self, object):
    object_id = None
    try:
      r = self.objects.update_one({"file": object['file']},
                                  {"$set": object},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      object_id = str(r.raw_result['upserted'])

    return object_id

  def get_objects_by_category(self, category,  offset=0, limit=50):
    query = {"category_class":category}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_category_name(self, category_name,  offset=0, limit=50):
    query = {"category_name":category_name}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_color(self, color,  offset=0, limit=50):
    query = {"color_class":color}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_age(self, age,  offset=0, limit=50):
    query = {"age_class":age}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_sex(self, sex,  offset=0, limit=50):
    query = {"sex_class":sex}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_texture(self, texture,  offset=0, limit=50):
    query = {"texture_class":texture}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_fabric(self, fabric,  offset=0, limit=50):
    query = {}
    query['fabric_class'] = {'$in': [fabric]}
    # db.getCollection('images').find({'fabric_class': {'$in': ['feather']}, '$where': 'this.fabric_class.length>1'})

    try:
      r = self.objects.find(query).where('this.fabric_class.length>1').skip(offset).limit(limit)
      # r = self.objects.find(query)
    except Exception as e:
      print(e)
    return list(r)

  def get_objects_by_shape(self, shape,  offset=0, limit=50):
    query = {"shape_class":shape}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_style(self, style,  offset=0, limit=50):
    query = {"style_class":style}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_objects_by_look(self, look,  offset=0, limit=50):
    query = {"look_class":look}

    try:
      r = self.objects.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def update_object(self, object):
    try:
      r = self.objects.update_one({"_id": object['_id']},
                                  {"$set": object})
    except Exception as e:
      print(e)
      return None

    return r.raw_result

  def update_objects(self, objects):
    try:
      bulk = self.objects.initialize_unordered_bulk_op()
      for i in range(0, len(objects)):
        bulk.find({'name': objects[i]['name']}).update({'$set': objects[i]})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)
