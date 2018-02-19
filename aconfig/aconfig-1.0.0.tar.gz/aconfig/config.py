from os import getcwd, listdir, path
import yaml
import json

class Config:
    class __Config:
        def __init__(self):
            self.base_dir = path.realpath(getcwd() + '/config')
            self.data = {}
            self.load()
        def load(self):
            for file in listdir(self.base_dir):
                if file.endswith('.json'):
                    self.loadJSON(self.base_dir, file)
                if file.endswith('.yml') or file.endswith('.yaml'):
                    self.loadYAML(self.base_dir, file)
                if file.endswith('.ini'):
                    print('ini')
        def loadJSON(self, dir, filename):
            name = filename[:filename.find('.json')]
            if name in self.data:
                name = name + '.json'
            with open(dir + '/' + filename) as file:
                data = json.loads(file.read())
            self.loadData(name, data)
        def loadYAML(self, dir, filename):
            if '.yaml' in filename:
                name = filename[:filename.find('.yaml')]
            else:
                name = filename[:filename.find('.yml')]
            if name in self.data:
                name = name + '.yaml'
            with open(dir + '/' + filename) as file:
                data = yaml.load(file.read())
            self.loadData(name, data)
        def loadData(self, name, data):
            if name != '':
                self.data[name] = data
            for key, value in data.items():
                field = key
                if name != '':
                    field = name + '.' + key
                if isinstance(value, dict):
                    self.loadData(field, value)
                else:
                    self.data[field] = value
                    
        def get(self, name):
            return self.data[name]
    instance = None
    def __init__(self):
        instance = self.newInstance()
    def newInstance():
        Config.instance = Config.__Config()
    def getInstance():
        if not Config.instance:
            Config.newInstance()
        return Config.instance
    def get(name):
        instance = Config.getInstance()
        return instance.get(name)

def config(name):
    return Config.get(name=name)