class MarkUpContainer(object):
    def __init__(self, inline_keyboard=None):
        self.inline_keyboard = inline_keyboard

    def get_data(self):
        data = {}
        if hasattr(self, 'inline_keyboard') and self.inline_keyboard:
            data['inline_keyboard'] = []

            for inline in self.inline_keyboard:
                temp = []
                for sub_inline in inline:
                    temp.append(sub_inline.get_data())
                data['inline_keyboard'].append(temp)

        return data


class Button(object):
    def __init__(self, text):
        self.text = text

    def get_data(self):
        if self.text is None:
            raise ValueError('The button title value are required')

        data = {
            'text': self.text
        }

        if hasattr(self, 'url') and self.url:
            data['url'] = self.url

        if hasattr(self, 'callback_data') and self.callback_data:
            data['callback_data'] = self.callback_data

        return data


class UrlButton(Button):
    def __init__(self, text, url):
        self.url = url
        super(UrlButton, self).__init__(text=text)


class CallbackButton(Button):
    def __init__(self, text, callback_data):
        self.callback_data = callback_data
        super(CallbackButton, self).__init__(text=text)
