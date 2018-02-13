from marshmallow import Schema, SchemaOpts, pre_dump


class Serializer(Schema):
    
    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
