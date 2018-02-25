from requests import Session

from .const import API_PATH, BASE_PATH, DEFAULT_LIMIT
from .models import Item, Updates, User


class HackerNews:
    def __init__(self, base_path=BASE_PATH, session=None):
        self.base_path = base_path
        self.session = session or Session()

    def ask(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['ask']), limit)

    def best(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['best']), limit)

    def get(self, path):
        return self.session.get('/'.join((self.base_path, path))).json()

    def item(self, id_):
        return Item(id_, self)

    def iterate_list(self, items, limit):
        items = iter(items)
        i = 0
        for item in items:
            if limit is None or i < limit:
                yield self.item(item)
                i += 1
            else:
                break

    def jobs(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['job']), limit)

    def max_item(self):
        # noinspection SpellCheckingInspection
        return self.item(self.get(API_PATH['maxitem']))

    def new(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['new']), limit)

    def show(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['show']), limit)

    def top(self, limit=DEFAULT_LIMIT):
        return self.iterate_list(self.get(API_PATH['top']), limit)

    def updates(self):
        return Updates(self.get(API_PATH['updates']), self)

    def user(self, name):
        return User(name, self)
