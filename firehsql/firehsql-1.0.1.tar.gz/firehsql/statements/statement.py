class Statement(object):

    schema = None

    def __init__(self, schema):
        self.schema = schema


    def get_data(self):
        return []


    def __str__(self):
        return ''


    @property
    def data(self):
        return self.get_data()
