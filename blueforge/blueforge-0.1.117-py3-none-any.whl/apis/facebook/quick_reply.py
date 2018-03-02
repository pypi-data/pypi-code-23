class QuickReplyItem(object):
    def get_data(self):
        if not self.content_type:
            raise ValueError('The content type is required.')
        elif self.content_type == 'text' and not self.title:
            raise ValueError('If the content type is text then the title value is required.')

        data = {
            'content_type': self.content_type
        }

        if self.title:
            data['title'] = self.title

        if self.image_url:
            data['image_url'] = self.image_url

        if self.payload:
            data['payload'] = self.payload

        return data


class QuickReplyLocationItem(QuickReplyItem):
    content_type = 'location'

    def __init__(self, image_url=None):
        self.image_url = image_url


class QuickReplyTextItem(QuickReplyItem):
    content_type = 'text'

    def __init__(self, title=None, payload=None, image_url=None):
        self.title = title
        self.payload = payload
        self.image_url = image_url


class QuickReply(object):
    def __init__(self, quick_reply_items):
        if not isinstance(quick_reply_items, list):
            raise ValueError('quick_reply_item should be list of QuickReplyItem object. ')
        self.quick_reply_items = quick_reply_items

    def get_data(self):
        return [quick_reply_item.get_data() for quick_reply_item in self.quick_reply_items]
