class EditMessage(object):
    def __init__(self, reply_markup=None):
        self.reply_markup = reply_markup

    def get_method(self):
        return self.method

    def get_data(self):
        data = {}

        if hasattr(self, 'reply_markup') and self.reply_markup:
            data['reply_markup'] = self.reply_markup.get_data()

        if hasattr(self, 'text') and self.text:
            data['text'] = self.text

        if hasattr(self, 'parse_mode') and self.parse_mode:
            data['parse_mode'] = self.parse_mode

        if hasattr(self, 'disable_web_page_preview') and self.disable_web_page_preview:
            data['disable_web_page_preview'] = self.disable_web_page_preview

        if hasattr(self, 'caption') and self.caption:
            data['caption'] = self.caption

        return data


class EditMessageText(EditMessage):
    method = 'editMessageText'

    def __init__(self, text, parse_mode=None, disable_web_page_preview=None, reply_markup=None):
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        super(EditMessageText, self).__init__(reply_markup=reply_markup)


class EditMessageCaption(EditMessage):
    method = 'editMessageCaption'

    def __init__(self, caption=None, reply_markup=None):
        self.caption = caption
        super(EditMessageCaption, self).__init__(reply_markup=reply_markup)


class EditMessageReplyMarkup(EditMessage):
    method = 'editMessageReplyMarkup'

    def __init__(self, reply_markup=None):
        super(EditMessageReplyMarkup, self).__init__(reply_markup=reply_markup)
