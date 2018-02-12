import json

class JsonBase(object):
    def toJson(self):
        return json.dumps(self, default=self.obj_dict)

    def toJsonObject(self):
        jsonText = json.dumps(self, default=self.obj_dict)
        return json.loads(jsonText)

    def obj_dict(self, obj):
        return obj.__dict__

class JsonHelper(object):
    def toJson(self, obj):
        return json.dumps(obj, default=self.obj_dict)

    def toJsonObject(self, obj):
        jsonText = json.dumps(obj, default=self.obj_dict)
        return json.loads(jsonText)

    def obj_dict(self, obj):
        return obj.__dict__
