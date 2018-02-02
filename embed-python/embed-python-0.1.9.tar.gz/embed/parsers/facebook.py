from . import generic


class Parser(generic.Parser):
    oembed_api_url = 'https://www.facebook.com/plugins/post/oembed.json/?url={url}'

    def get_embed(self):
        response = self.fetch_oembed()

        if response:
            return {
                "id": None,
                "url": response['url'],
                "type": response['type'],
                'duration': self.embed_duration(),
                "height": response['height'],
                "width": response['width'],
                "ratio": None,
                "html_code": response['html']
            }
