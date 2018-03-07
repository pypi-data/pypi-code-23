from bson.objectid import ObjectId
from stylelens_product.database import DataBase

class Products(DataBase):
  def __init__(self):
    super(Products, self).__init__()
    self.products = self.db.products

  def add_product(self, product):
    object_id = None
    query = {"host_code": product['host_code'], "product_no": product["product_no"]}
    try:
      r = self.products.update_one(query,
                                  {"$set": product},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      product_id = str(r.raw_result['upserted'])

    return product_id

  def add_products(self, products):
    try:
      r = self.products.insert(products)
    except Exception as e:
      print(e)

    return r

  def get_product_by_id(self, product_id):
    try:
      r = self.products.find_one({"_id": ObjectId(product_id)})
    except Exception as e:
      print(e)

    return r

  def get_products_by_hostcode_and_version_id(self,
                                              host_code, version_id=None,
                                              is_processed=None,
                                              is_classified=None,
                                              offset=0, limit=100):
    query = {}
    query['host_code'] = host_code

    if version_id is not None:
      query['version_id'] = version_id

    if is_processed is not None:
      query['is_processed'] = is_processed

    if is_classified is not None:
      query['is_classified'] = is_classified

    try:
      r = self.products.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_products_by_version_id(self,
                                  version_id,
                                  is_available=None,
                                  is_processed=None,
                                  is_classified=None,
                                  is_processed_for_text_class_model=None,
                                  is_classified_for_text=None,
                                  offset=0, limit=100):
    query = {}
    query['version_id'] = version_id

    if is_processed is False:
      query['$or'] = [{'is_processed':False}, {'is_processed':None}]
    elif is_processed is True:
      query['is_processed'] = True

    if is_available is False:
      query['$or'] = [{'is_available':False}, {'is_available':None}]
    elif is_available is True:
      query['is_available'] = True

    if is_classified is False:
      query['$or'] = [{'is_classified':False}, {'is_classified':None}]
    elif is_classified is True:
      query['is_classified'] = True

    if is_processed_for_text_class_model is False:
      query['$or'] = [{'is_processed_for_text_class_model':False}, {'is_processed_for_text_class_model':None}]
    elif is_processed_for_text_class_model is True:
      query['is_processed_for_text_class_model'] = True

    if is_classified_for_text is False:
      query['$or'] = [{'is_classified_for_text': False}, {'is_classified_for_text': None}]
    elif is_classified_for_text is True:
      query['is_classified_for_text'] = True

    try:
      r = self.products.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_size_not_classified(self, version_id):
    query = {}
    query['version_id'] = version_id
    query['$or'] = [{'is_classified':False}, {'is_classified':None}]

    try:
      count = self.products.find(query).count()
    except Exception as e:
      print(e)

    return count

  def get_size_products(self, version_id,
                        is_available=None,
                        is_processed=None,
                        is_classified=None,
                        is_processed_for_text_class_model=None,
                        is_classified_for_text=None):
    query = {}
    query['version_id'] = version_id

    if is_available is not None:
      query['is_available'] = is_available

    if is_processed is not None:
      query['is_processed'] = is_processed

    if is_processed_for_text_class_model is not None:
      query['is_processed_for_text_class_model'] = is_processed_for_text_class_model

    if is_classified is not None:
      query['is_classified'] = is_classified

    if is_classified_for_text is not None:
      query['is_classified_for_text'] = is_classified_for_text

    try:
      count = self.products.find(query).count()
    except Exception as e:
      print(e)

    return count

  def get_products_by_keyword(self, keyword,
                              only_text=True,
                              is_processed_for_text_class_model=None,
                              offset=0,
                              limit=100):
    query = {}
    if is_processed_for_text_class_model is None:
      query['$or'] = [{'$text':{'$search':"\"" + keyword + "\""}}]
    elif is_processed_for_text_class_model is False:
      query['$and'] = [{'$text':{'$search':"\"" + keyword + "\""},
                       '$or':[{'is_processed_for_text_class_model': {'$exists': 0}},
                              {'is_processed_for_text_class_model': False}]
                       }]
    #
    #
    # if is_processed_for_text_class_model is None:
    #   query['$or'] = [{"name": {"$regex": keyword, "$options": 'x'}},
    #                   {'cate': {"$regex": keyword, "$options": 'x'}}]
    #
    # if is_processed_for_text_class_model is False:
    #   query['$or'] = [{"name": {"$regex": keyword, "$options": 'x'},
    #                  '$or':[{'is_processed_for_text_class_model': {'$exists': 0}},
    #                         {'is_processed_for_text_class_model': False}]
    #                  },
    #                 {'cate': {"$regex": keyword, "$options": 'x'},
    #                  '$or':[{'is_processed_for_text_class_model': {'$exists': 0}},
    #                         {'is_processed_for_text_class_model': False}]
    #                  }]

    try:
      if only_text is True:
        r = self.products.find(query, {'name':1, 'tags':1, 'cate':1}).skip(offset).limit(limit)
      else:
        r = self.products.find(query).skip(offset).limit(limit)

    except Exception as e:
      print(e)

    return list(r)

  def get_products_count_by_keyword(self, keyword,
                                    is_processed_for_text_class_model=None):
    query = {}
    # query['$or'] = [{"name": {"$regex": keyword, "$options": 'x'}},
    #                 {'cate': {"$regex": keyword, "$options": 'x'}}]
    if is_processed_for_text_class_model is None:
      query['$or'] = [{'$text':{'$search':"\"" + keyword + "\""}}]
    elif is_processed_for_text_class_model is False:
      query['$or'] = [{'$text':{'$search':keyword},
                       '$or':[{'is_processed_for_text_class_model': {'$exists': 0}},
                              {'is_processed_for_text_class_model': False}]
                       }]
    r = -1
    try:
      r = self.products.find(query).count()

    except Exception as e:
      print(e)

    return r

  def update_product_by_id(self, product_id, product):
    try:
      r = self.products.update_one({"_id": ObjectId(product_id)},
                                  {"$set": product})
    except Exception as e:
      print(e)

    return r.modified_count

  def update_products(self, products):
    try:
      bulk = self.products.initialize_unordered_bulk_op()
      for i in range(0, len(products)):
        bulk.find({'_id': products[i]['_id']}).update({'$set': products[i]})
      r = bulk.execute()
    except Exception as e:
      print(e)

  def update_product_by_hostcode_and_productno(self, product):
    query = {"host_code": product['host_code'], "product_no": product['product_no']}
    try:
      r = self.products.update_one(query,
                                  {"$set": product},
                                  upsert=True)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_product(self, product_id):
    query = {}
    query['_id'] = ObjectId(product_id)
    try:
      r = self.products.delete_one(query)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_old_products(self, version_id):
    query = {}
    query["version_id"] = {"$ne": version_id}

    try:
      r = self.products.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result

  def delete_products_by_hostcode_and_version_id(self, host_code, version_id, except_version=True):
    if except_version == True:
      query = {"host_code": host_code, "version_id": version_id}
    else:
      query = {"host_code": host_code, "version_id": {"$ne": version_id}}

    try:
      r = self.products.delete_many(query)
    except Exception as e:
      print(e)

    return r.raw_result

  def reset_product_as_not_object_classified(self, version_id=None):
    query = {}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.products.update_many(query, {"$unset":{'is_classified':1}})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result

  def reset_product_as_available(self, version_id=None):
    query = {}
    product = {"is_available": True}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.products.update_many(query, {"$set":product})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result

  def reset_product_is_processed_for_text_class_model(self, version_id=None):
    query = {}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.products.update_many(query, {"$unset":{'is_processed_for_text_class_model':1}})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result

  def reset_product_is_classified_for_text(self, version_id=None):
    query = {}

    if version_id is not None:
      query['version_id'] = version_id

    try:
      r = self.products.update_many(query, {"$unset":{'is_classified_for_text':1}})
      print(r)
    except Exception as e:
      print(e)
    return r.raw_result