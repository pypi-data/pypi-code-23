import re

class Content(object):
    def __init__(self,
                 data,
                 headers):
        self.data = data
        self.content_type = headers.get('content-type', None)
        content_disposition = headers.get('content-disposition', '')
        m = re.match('^attachment; filename="(?P<filename>[^"]*)"$', content_disposition)
        self.filename = m.group('filename') if m else None
        

    def __bytes__(self):
        return self.data
