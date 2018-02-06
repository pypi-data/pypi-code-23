from bson.objectid import ObjectId
from stylelens_dataset.database import DataBase

class Texts(DataBase):
  def __init__(self):
    super(Texts, self).__init__()
    self.texts = self.db.texts
    self.classes = self.db.text_classes

  def add_text(self, text):
    id = None
    query = {"text_code": text["text_code"], "text": text["text"]}
    try:
      r = self.texts.update_one(query, {"$set": text},
                                upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def get_texts(self, text_code,
                offset=0, limit=100):
    query = {"text_code": text_code}

    try:
      r = self.texts.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_classes(self, offset=0, limit=100):
    query = {}

    try:
      r = self.classes.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)
