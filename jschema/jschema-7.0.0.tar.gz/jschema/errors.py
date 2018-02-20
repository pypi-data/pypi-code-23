import json


class JrsError(Exception):
    pass


class JrsSchemaError(JrsError):
    pass


class JrsNodeError(JrsError):
    @staticmethod
    def make_message(message, node):
        return u"{}. node: {}, schema_id: {}".format(
            message,
            unicode(json.dumps(node.parent.value, indent=2, separators=(',', ': '))),
            node.root.key
        )

class JrsFormatingError(JrsError):
    pass
