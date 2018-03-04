import copy


class ResponseBuilder:

    def __init__(self):
        self.fallback = None
        self.color = None
        self.pretext = None
        self.author = None
        self.author_link = None
        self.author_icon = None
        self.title = None
        self.title_link = None
        self.text = None
        self.fields = []
        self.image_url = None
        self.thumb_url = None
        self.footer = None
        self.footer_icon = None
        self.ts = '{time}'
        self.attachment = True

        self.base = [
        {
            "fallback": self.fallback,
            "color": self.color,
            "pretext": self.pretext,
            "author_name": self.author,
            "author_link": self.author_link,
            "author_icon": self.author_icon,
            "title": self.title,
            "title_link": self.title_link,
            "text": self.text,
            "fields": self.fields,
            "image_url": self.image_url,
            "thumb_url": self.thumb_url,
            "footer": self.footer,
            "footer_icon": self.footer_icon,
            "ts": self.ts
        }
    ]

    def __clear_base(self):
        self.fallback = None
        self.color = None
        self.pretext = None
        self.author = None
        self.author_link = None
        self.author_icon = None
        self.title = None
        self.title_link = None
        self.text = None
        self.fields = []
        self.image_url = None
        self.thumb_url = None
        self.footer = None
        self.footer_icon = None
        self.ts = '{time}'
        self.attachment = True


    def add_field(self, title=None, value=None, short=True):
        field = {
                "title": title,
                "value": value,
                "short": short
            }

        for i in list(field):
            if not field[i]:
                field.pop(i, None)

        self.fields.append(field)

    def set_text(self, str):
        self.attachment = False
        self.text = str

    def extract(self):
        self.base = [
            {
                "fallback": self.fallback,
                "color": self.color,
                "pretext": self.pretext,
                "author_name": self.author,
                "author_link": self.author_link,
                "author_icon": self.author_icon,
                "title": self.title,
                "title_link": self.title_link,
                "text": self.text,
                "fields": self.fields,
                "image_url": self.image_url,
                "thumb_url": self.thumb_url,
                "footer": self.footer,
                "footer_icon": self.footer_icon,
                "ts": self.ts
            }
        ]

        for i in list(self.base[0]):
            if not self.base[0][i]:
                self.base[0].pop(i, None)

        if not self.attachment or not self.base:
            self.base = self.text

        res = self.base, self.attachment
        ret = copy.deepcopy(res)
        self.__clear_base()

        return ret

    def help(self):
        """
        A standard template for help messages
        """

        self.pretext = 'Hope this helps you out!'
        self.color = "#114c93"

    def error(self):
        """
        A template for error messages
        """

        self.pretext = 'ALERT'
        self.color = '#f90000'

    def succes(self):
        self.pretext = 'Here you go!'
        self.color = "#36a64f"