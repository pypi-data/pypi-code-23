import requests
from typing import Iterator, NewType

FM_BASE = 'https://fazlamesai.net/'

class Link:
    """Represents a link posted to fazlamesai.net."""
    def __init__(self):
        self.id = ''
        self.author_id = ''
        self.title = ''
        self.published_at = ''
        self.slug = ''
        self.comment_count = 0
        self.url = 0

class Client:
    """The client object is responsible for communicating with the fazlamesai
    API."""
    def __init__(self, api_key: str):
        """Creates a new Client object. Needs an API token, which can be
        acquired from https://fazlamesai.net/users/$USERNAME/tokens."""
        self.api_key = api_key
        self.sess = requests.Session()
        self.auth = {'Authorization': 'Bearer {}'.format(api_key)}

    def get_posts(self) -> Iterator[Link]:
        """Returns an iterator of posts from the fazlamesai frontpage."""
        url = FM_BASE + 'api/v1/links'
        links_json = self.sess.get(url, headers=self.auth).json()

        for link in links_json['data']:
            link_obj = Link()
            link_obj.id            = link['id']
            link_obj.author_id     = link['author_id']
            link_obj.title         = link['title']
            link_obj.published_at  = link['published_at']
            link_obj.slug          = link['slug']
            link_obj.comment_count = link['comments_count']
            link_obj.url           = link['url']

            yield link_obj
