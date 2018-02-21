import os
import boto3

class ssm(object):
  def __init__(self, params, parser=None, separator='/'):
    print("init")
    if type(params) is not list:
      raise TypeError("params must be of type list but is of type %s" % type(params))
    self.params = params
    self.parser = parser
    self.separator = separator
    self.client = boto3.client('ssm')
  def __call__(self, fn):
    print("call")
    def wrapped_fn(*args, **kwargs):
      print("before")
      params = self.client.get_parameters(Names=self.params,WithDecryption=True)
      for param in params.get('Parameters',[]):
        if self.parser is None:
          # Split parameter by separator removing the first level and converting to environment variable
          # e.g. /my-stack/db/password will return ['db','password'], which will get converted to DB_PASSWORD
          parts = param['Name'].strip(self.separator).split(self.separator)
          if len(parts) > 1:
            key = '_'.join(parts[1:]).upper()
            os.environ[key] = param['Value']
          # If the parameter has no "levels" then just use the parameter name as the environment variable as is
          # e.g. if the parameter name is my_stack then the environment variable my_stack will be set
          else:
            os.environ[parts[0]] = param['Value']
        else:
          parsed = self.parser(param['Value'])
          os.environ[parsed[0]] = parsed[1]
      fn(*args, **kwargs)
    return wrapped_fn