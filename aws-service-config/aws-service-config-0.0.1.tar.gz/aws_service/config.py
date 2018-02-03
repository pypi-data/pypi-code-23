import os
import boto3

from enum import Enum

class Source(Enum):
    SSM = 'ssm'
    DYNAMODB = 'dynamodb'


class ConfigBuilder():
    _raw_config = {}
    _config = {}
    _env = 'local'
    _ssm_client = None
    _dynamodb = None
    _source = Source.DYNAMODB

    def __init__(self, source=Source.DYNAMODB, env=None):
        if not env:
            self._env = os.getenv('ENVIRONMENT', 'local').lower()
        else:
            self._env = env.lower()

        if Source.SSM == source:
            self._ssm_client = boto3.resource('ssm')
        else:
            self._config_table = "{0}_{1}".format(self._env, "config")
            self._dynamodb = boto3.resource('dynamodb')
            self._raw_config = self._dynamodb.Table(self._config_table).get_item(Key={"id": self._env})


    def dynamodb_table(self, table_name, config_name=None):
        if not config_name:
            config_name = table_name

        self._config[config_name] = self._dynamodb.Table(table_name)
        return self


    def table(self, table_name, config_name=None):
        self.dynamodb_table(table_name, config_name)
        return self


    def sns(self):
        self._config['sns'] = boto3.client('sns')
        return self


    def sqs(self):
        self._config['sqs'] = boto3.client('sqs')
        return self


    def get_parameter(self, parameter_name, path=''):
        return self._get_db_parameter(parameter_name, path)


    def parameter(self, parameter_name, config_name=None, path=''):
        if not config_name:
            config_name = parameter_name

        if self._source == Source.SSM:
            self._config[config_name] = self._get_parameter(self._ssm_client, self._env, path, parameter_name)
        else:
            self._config[config_name] = self._get_db_parameter(parameter_name, path)
        return self


    def build_trade_api_config(self):
        self._config['trade_apis'] = {}

        if self._source == Source.SSM:
            params = self._get_parameters(self._ssm_client, self._env, key='trade_apis')
            for exchange in params:
                self._config['trade_apis'][exchange['Name'].split('/')[-1]] = exchange['Value']
        else:
            self._config['trade_apis'] = self._raw_config.get('trade_config').get('apis')
        return self


    def _get_db_parameter(self, parameter_name, path=''):
        if path and path != '':
            temp_config = self._raw_config
            keys = path.split('/')
            for key in keys:
                temp_config = temp_config.get(key)
            return temp_config.get(parameter_name)

        return self._raw_config.get(parameter_name)


    def _get_parameters(self, client, env, path='', key=''):
        path = "/%s%s/%s" % (env, path, key)
        return client.get_parameters_by_path(
            Path=path,
            Recursive=False,
            WithDecryption=False,
            MaxResults=10
        )['Parameters']


    def _get_parameter(self, client, env, path='', key=''):
        params = self._get_parameters(client, env, path, '')
        param = next((item for item in params if item['Name'] == "/%s%s/%s" % (env, path, key)), None)
        if not param:
            print("Parameter '%s' was not found!" % key)
            raise Exception("Parameter '%s' was not found!" % key)
        else:
            if param['Type'] == 'StringList':
                return param['Value'].split(',')
            else:
                return param['Value']

    def get_config(self):
        return self._config
