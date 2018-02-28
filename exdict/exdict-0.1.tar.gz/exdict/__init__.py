
class Exdict(dict):
    """
    Behaves like a dict and a class
    """
    def __getattr__(self, key):
        if key in ["__getattr__", "__setattr__"] + dir(dict):
            return None
            #TODO: use super(dict,self).__getattr__(key)
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __dir__(self):
        return dir(super(Exdict,self)) + self.keys()

    @classmethod
    def from_dict(cls, dct):
        d = Exdict()
        if isinstance(dct, list):
            return [cls.from_dict(x) for x in dct]
        assert isinstance(dct, dict)
        for k,v in dct.iteritems():
            if isinstance(v, dict):
                d[k] = cls.from_dict(v)
            else:
                d[k] = v
        return d


    @classmethod
    def from_yaml(cls, filename):
        try:
            import yaml
        except ImportError:
            raise Exception("YAML not installed! Install it through 'pip install PyYAML'")
        d = yaml.load(open(filename).read())
        return cls.from_dict(d)

