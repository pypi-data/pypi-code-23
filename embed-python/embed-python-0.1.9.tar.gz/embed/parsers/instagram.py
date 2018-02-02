# -*- coding: utf-8 -*-
from . import generic


class Parser(generic.Parser):
    oembed_api_url = 'https://api.instagram.com/oembed/?url={url}'

    def get_embed(self):
        response = self.fetch_oembed()

        if response:
            print(response)
            return {
                "id": None,
                "url": self.url,
                "type": response['type'],
                'duration': self.embed_duration(),
                "height": response['height'],
                "width": response['width'],
                "ratio": None,
                "html_code": response['html']
            }
