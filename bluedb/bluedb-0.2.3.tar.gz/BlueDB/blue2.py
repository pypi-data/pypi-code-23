import ujson
from collections.abc import MutableMapping, MutableSequence

class Blue(MutableMapping):

    def __init__(self, name):
        self.name = name
        self.file = name+'.blue'
        self.body = {}
        try:
            with open(self.file, 'r') as fp:
                data = ujson.load(fp)
                for i in data.keys():
                    if type(data[i]) is dict:
                        blue = _BlueDict(i, data[i], self)
                        self.body[i] = data[i]
                    elif type(data[i]) is list:
                        blue = _BlueList(i, data[i], self)
                        self.body[i] = data[i]
                    else:
                        self.body[i] = data[i]
        except:
            with open(self.file, 'w') as fp:
                ujson.dump({}, fp)

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

    def __len__(self):
        return len(self.body)

    def __iter__(self):
        return iter(self.body)

    def __setitem__(self, key, value):
        if type(value) is dict:
            blue = _BlueDict(key, value, self)
            self.body[key] = value
        elif type(value) is list:
            blue = _BlueList(key, value, self)
            self.body[key] = value
        else:
            self.body[key] = value
        with open(self.file, 'w') as fp:
            ujson.dump(self.body, fp)

    def __getitem__(self, key):
        try:
            return self.body[key]
        except:
            with open(self.file, 'r') as fp:
                data = ujson.load(fp)
                self.body[key] = data[key]
            return self.body[key]

    def __delitem__(self, key):
        del self.body[key]
        with open(self.file, 'w') as fp:
            ujson.dump(self.body, fp)

class _BlueDict(MutableMapping):

    def __init__(self, key, value, previous):
        self.key = key
        self.body = {}
        self.previous = previous
        for i in value.keys():
            if type(value[i]) is dict:
                blue = _BlueDict(i, value[i], self)
                self.body[i] = blue
            elif type(value[i]) is list:
                blue = _BlueList(i, value[i], self)
                self.body[i] = blue
            else:
                self.body[i] = value[i]

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

    def __iter__(self):
        return iter(self.body)

    def __len__(self):
        return len(self.body)

    def __setitem__(self, key, value):
        if type(value) is dict:
            blue = _BlueDict(key, value, self)
            self.body[key] = blue
        elif type(value) is list:
            blue = _BlueList(key, value, self)
            self.body[key] = blue
        else:
            self.body[key] = value
        self.previous.__setitem__(self.key, self.body)

    def __getitem__(self, key):
        return self.body[key]

    def __delitem__(self, key):
        del self.body[key]

class _BlueList(MutableSequence):

    def __init__(self, key, value, previous):
        self.key = key
        self.body = []
        self.previous = previous

        for i in value:
            self.append(i)

    def __repr__(self):
        return str(self.body)

    def __str__(self):
        return str(self.body)

    def __iter__(self):
        return iter(self.body)

    def __len__(self):
        return len(self.body)

    def __setitem__(self, index, value):
        if type(value) is dict:
            blue = _BlueDict(index, value, self)
            self.body[index] = value
        elif type(value) is list:
            blue = _BlueList(index, value, self)
            self.body[index] = value
        else:
            self.body[index] = value
        self.previous.__setitem__(self.key, self.body)

    def __getitem__(self, index):
        return self.body[key]

    def __delitem__(self, index):
        del self.body[key]
        self.previous.__setitem__(self.key, self.body)

    def insert(self, index, value):
        self.body.insert(index, value)
