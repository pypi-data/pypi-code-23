from stylelens_product.database import DataBase

class Hosts(DataBase):
  def __init__(self):
    super(Hosts, self).__init__()
    self.hosts = self.db.hosts

  def add_host(self, host):
    id = None
    query = {}
    query['host_code'] = host['host_code']

    try:
      r = self.hosts.update_one(query,
                               {"$set": host},
                               upsert=True)
    except Exception as e:
      print(e)
      return None

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def get_hosts(self,
                host_group=None,
                crawl_status=None,
                offset=0, limit=100):
    query = {}

    if host_group is not None:
      query['host_group'] = host_group

    if crawl_status is not None:
      query['crawl_status'] = crawl_status

    try:
      r = self.hosts.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)
      return None

    return list(r)

  def update_host(self, host):
    query = {"host_code": host['host_code']}
    try:
      r = self.hosts.update_one(query,
                                {"$set": host},
                                upsert=True)
    except Exception as e:
      print(e)
      return None

    return r.raw_result
