from .const import API_PATH, DEFAULT_LIMIT, ITEM_BASE_URL, USER_BASE_URL


class Item:
    # noinspection SpellCheckingInspection
    ITEM_ATTRS = ('kids', 'parts',)

    @property
    def content(self):
        """Attempt to find and return the relevant content from any type of item."""
        if hasattr(self, 'text'):
            return self.text
        if hasattr(self, 'url'):
            return self.url
        if hasattr(self, 'title'):
            return self.title
        return ''

    @property
    def link(self):
        """Get a link to the item on HN."""
        return ITEM_BASE_URL.format(id=self.id)

    def __eq__(self, other):
        if isinstance(other, (int, str)):
            return other == self.id or str(self.id) == str(other)
        return hasattr(other, 'id') and self == other.id  # light recursion...

    def __init__(self, id_, hn, data=None):
        self._hn = hn
        self.id = id_
        self._loaded = False
        self._private = dict()
        if data:
            self._populate(data)

    def __getattr__(self, item):
        if not self._loaded:
            self._load()
            return getattr(self, item)

        raise AttributeError('{!r} object has no attribute {!r}'.format(self.__class__.__name__, item))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.id)

    def _ensure_loaded(self):
        if not self._loaded:
            self._load()

    def _iter_helper(self, name, limit):
        self._ensure_loaded()
        return self._hn.iterate_list(self._private[name], limit)

    def _load(self):
        data = self._hn.get(API_PATH['item'].format(id=self.id))
        self._populate(data)

    def _populate(self, data):
        for key, value in data.items():
            if key == 'id':
                continue
            if key in Item.ITEM_ATTRS:
                self._private[key] = value
                continue
            if key == 'by':
                value = self._hn.user(value)
            if key in ('parent', 'poll'):
                value = self._hn.item(value)
            self.__setattr__(key, value)
        self._loaded = True

    def kids(self, limit=DEFAULT_LIMIT):
        return self._iter_helper('kids', limit)

    def parts(self, limit=DEFAULT_LIMIT):
        return self._iter_helper('parts', limit)


class User:
    # noinspection SpellCheckingInspection
    ITEM_ATTRS = ('submitted',)

    @property
    def link(self):
        """Get a link to the item on HN."""
        return USER_BASE_URL.format(user=self.name)

    def __eq__(self, other):
        if isinstance(other, (int, str)):
            return other == self.name
        return hasattr(other, 'name') and other.name == self.name

    def __getattr__(self, item):
        if not self._loaded:
            self._load()
            return getattr(self, item)

        raise AttributeError('{!r} object has no attribute {!r}'.format(self.__class__.__name__, item))

    def __init__(self, name, hn, data=None):
        self.name = name
        self._hn = hn
        self._loaded = False
        self._private = dict()
        if data:
            self._populate(data)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.name)

    def _load(self):
        data = self._hn.get(API_PATH['user'].format(user=self.name))
        if data is None:
            raise ValueError('User {!r} does not exist'.format(self.name))
        self._populate(data)

    def _populate(self, data):
        for key, value in data.items():
            if key == 'name':
                continue
            if key in User.ITEM_ATTRS:
                self._private[key] = value
                continue
            self.__setattr__(key, value)
        self._loaded = True

    def submitted(self, limit=DEFAULT_LIMIT):
        if not self._loaded:
            self._load()
        return self._hn.iterate_list(self._private['submitted'], limit)


class Updates:
    def __init__(self, data, hn):
        self._items = data['items']
        self._profiles = data['profiles']
        self._hn = hn

    def items(self, limit=DEFAULT_LIMIT):
        return self._hn.iterate_list(self._items, limit)

    def profiles(self, limit=DEFAULT_LIMIT):
        users = iter(self._profiles)
        i = 0
        for user in users:
            if limit is None or i < limit:
                yield self._hn.user(user)
                i += 1
            else:
                break
