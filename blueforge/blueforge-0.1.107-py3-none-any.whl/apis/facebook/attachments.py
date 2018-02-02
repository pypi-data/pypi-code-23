class Attachment(object):
    def __init__(self, payload=None):
        self.payload = payload

    def get_data(self):
        if type(self.payload) is dict:
            return {'type': self.type, 'payload': self.payload}

        return {'type': self.type, 'payload': self.payload.get_data()}


class TemplateAttachment(Attachment):
    type = 'template'

    def __init__(self, payload):
        super(TemplateAttachment, self).__init__(payload)


class ImageAttachment(Attachment):
    type = 'image'

    def __init__(self, url=None, is_reusable=False):
        payload = {
            'url': url,
            'is_reusable': is_reusable
        }

        super(ImageAttachment, self).__init__(payload)


class AudioAttachment(Attachment):
    type = 'audio'

    def __init__(self, url=None, is_reusable=False):
        payload = {
            'url': url,
            'is_reusable': is_reusable
        }

        super(ImageAttachment, self).__init__(payload)


class VideoAttachment(Attachment):
    type = 'video'

    def __init__(self, url=None, is_reusable=False):
        payload = {
            'url': url,
            'is_reusable': is_reusable
        }

        super(ImageAttachment, self).__init__(payload)


class FileAttachment(Attachment):
    type = 'file'

    def __init__(self, url=None, is_reusable=False):
        payload = {
            'url': url,
            'is_reusable': is_reusable
        }

        super(ImageAttachment, self).__init__(payload)
