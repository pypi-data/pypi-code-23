class Button(object):
    def __init__(self, title=None):
        self.title = title

    def get_data(self):
        if self.button_type is None or self.title is None:
            raise ValueError('The button type and title value are required')

        data = {
            'type': self.button_type
        }

        if self.title is not None:
            data['title'] = self.title

        if self.button_type == 'web_url':
            if self.url is None:
                raise ValueError('The url value is required')

            data['url'] = self.url

            if self.webview_height_ratio:
                data['webview_height_ratio'] = self.webview_height_ratio
            if self.messenger_extensions:
                data['messenger_extensions'] = self.messenger_extensions
            if self.fallback_url:
                data['fallback_url'] = self.fallback_url

        elif self.button_type == 'postback' or self.button_type == 'phone_number':
            if self.payload:
                data['payload'] = self.payload
        elif self.button_type == 'element_share':
            if self.share_contents:
                data['share_contents'] = self.share_contents

        return data


class UrlButton(Button):
    button_type = 'web_url'

    def __init__(self, url=None, title=None, webview_height_ratio=None, messenger_extensions=None, fallback_url=None):
        self.url = url
        self.webview_height_ratio = webview_height_ratio
        self.messenger_extensions = messenger_extensions
        self.fallback_url = fallback_url
        super(UrlButton, self).__init__(title)


class PostBackButton(Button):
    button_type = 'postback'

    def __init__(self, title=None, payload=None):
        self.title = title
        self.payload = payload
        super(PostBackButton, self).__init__(title)


class ShareButton(Button):
    button_type = 'element_share'

    def __init__(self, title=None, share_contents=None):
        self.share_contents = share_contents
        super(ShareButton, self).__init__(title)


class PhoneNumberButton(Button):
    button_type = 'phone_number'

    def __init__(self, title=None, payload=None):
        self.title = title
        self.payload = payload
        super(PhoneNumberButton, self).__init__(title=title)
