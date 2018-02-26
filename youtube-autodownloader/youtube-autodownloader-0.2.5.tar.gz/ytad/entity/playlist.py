import dateutil.parser

import ytad.entity._entity_base


class Playlist(ytad.entity._entity_base.EntityBase):
    @property
    def id(self):
        return self.data['id']

    @property
    def title(self):
        return self.data['snippet']['title']

    @property
    def description(self):
        return self.data['snippet']['description']

    @property
    def published_at(self):
        return dateutil.parser.parse(self.data['snippet']['publishedAt'])

    @property
    def tags(self):
        return self.data['snippet']['tags']

    @property
    def item_count(self):
        """Only available when the "contentDetails" part is requested."""

        return self.data['contentDetails']['itemCount']

    def __str__(self):
        return "Playlist<ID=[{}] TITLE=[{}]>".format(self.id, self.title)
