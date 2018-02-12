from fidataset import _logic as _lg


def fetch(name):
    return _lg.fetch(name)
  
def list_datasets():
    return _lg.list_datasets()

def search(txt):
    return _lg.search(txt)
