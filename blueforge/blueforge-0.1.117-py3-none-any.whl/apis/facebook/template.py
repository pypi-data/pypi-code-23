class Template(object):
    def get_data(self):
        if (self.template_type == 'list' or self.template_type == 'open_graph' or self.template_type == 'generic') \
                and not self.elements:
            raise ValueError('The elements is required.')
        data = {
            'template_type': self.template_type,
        }

        if hasattr(self, 'elements'):
            if len(self.elements) > 10:
                raise RuntimeWarning('The Element exceeds the maximum of 10.')

            data['elements'] = [element.get_data() for element in self.elements]

        if hasattr(self, 'url'):
            if self.url:
                data['url'] = self.url

        if hasattr(self, 'top_element_style'):
            if self.top_element_style:
                data['top_element_style'] = self.top_element_style

        if hasattr(self, 'text'):
            if self.text:
                data['text'] = self.text

        if hasattr(self, 'buttons'):
            if self.buttons:
                if len(self.buttons) > 3:
                    raise RuntimeWarning('The Buttons exceeds the maximum of 3.')

                data['buttons'] = [button.get_data() for button in self.buttons]

        return data


class ButtonTemplate(Template):
    template_type = 'button'

    def __init__(self, url=None, text=None, buttons=None):
        self.url = url
        self.text = text
        self.buttons = buttons


class GenericTemplate(Template):
    template_type = 'generic'

    def __init__(self, elements=None):
        self.elements = elements


class ListTemplate(Template):
    template_type = 'list'

    def __init__(self, elements=None, top_element_style=None, buttons=None):
        self.elements = elements
        self.top_element_style = top_element_style
        self.buttons = buttons


class OpenGraphTemplate(Template):
    template_type = 'open_graph'

    def __init__(self, elements=None):
        self.elements = elements
