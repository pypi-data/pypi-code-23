from bson.objectid import ObjectId
from stylelens_dataset.database import DataBase

class Images(DataBase):
  def __init__(self):
    super(Images, self).__init__()
    self.labels = self.db.labels

  def get_label_by_id(self, id):
    query = {"_id": ObjectId(id)}
    try:
      r = self.labels.find_one(query)
    except Exception as e:
      print(e)

    return r

  def get_label(self, index, clazz):
    query = {"index": index, "clazz": clazz}
    try:
      r = self.labels.find_one(query)
    except Exception as e:
      print(e)

    return r

  def add_label(self, label):
    label_id = None
    query = {"index": label["index"], "clazz": label["clazz"]}
    try:
      r = self.labels.update_one(query,
                                  {"$set": label},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      label_id = str(r.raw_result['upserted'])

    return label_id

  def get_labels(self, clazz,  offset=0, limit=50):
    query = {"clazz":clazz}

    try:
      r = self.labels.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def update_label(self, label):
    try:
      r = self.labels.update_one({"_id": label['_id']},
                                  {"$set": label})
    except Exception as e:
      print(e)
      return None

    return r.raw_result

  def update_labels(self, labels):
    try:
      bulk = self.labels.initialize_unordered_bulk_op()
      for i in range(0, len(labels)):
        bulk.find({'_id': labels[i]['_id']}).update({'$set': labels[i]})
      r = bulk.execute()
      print(r)
    except Exception as e:
      print(e)
