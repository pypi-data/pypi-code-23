class Element(object):
    def __init__(self, title, item_url=None,
                 image_url=None, subtitle=None, buttons=None, default_action=None):
        self.title = title
        self.item_url = item_url
        self.image_url = image_url
        self.subtitle = subtitle
        self.buttons = buttons
        self.default_action = default_action

    def get_data(self):
        data = {
            'title': self.title,
        }

        if self.default_action:
            data['default_action'] = self.default_action

        if self.buttons:
            if len(self.buttons) > 3:
                raise RuntimeWarning('The Button\' element exceeds the maximum of 3.')

            data['buttons'] = [
                button.get_data() for button in self.buttons
            ]

        if self.item_url:
            data['item_url'] = self.item_url

        if self.image_url:
            data['image_url'] = self.image_url

        if self.subtitle:
            data['subtitle'] = self.subtitle

        return data
