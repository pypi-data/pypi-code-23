from stylelens_dataset.database import DataBase

class Categories(DataBase):
  def __init__(self):
    super(Categories, self).__init__()
    self.categories = self.db.categories
    self.classes = self.db.category_classes

  def get_classes(self, offset=0, limit=100):
    query = {}

    try:
      r = self.classes.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def add_category(self, category):
    id = None
    query = {"name": category["name"],
             "class_code": category["class_code"]}
    try:
      r = self.categories.update_one(query, {"$set": category},
                                upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def get_categories(self, offset=0, limit=100):
    try:
      r = self.categories.find().skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)
