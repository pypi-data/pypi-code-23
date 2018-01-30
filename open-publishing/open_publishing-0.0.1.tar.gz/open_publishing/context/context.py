import logging

from open_publishing.gjp import GJP

from .documents import Documents
from .users import Users
from .orders import Orders
from .order_fulfillments import OrderFulfillments
from .accounts import Accounts
from .events import Events
from .me import Me
from .onix import Onix
from .imprints import Imprints
from .genres import Genres
from .isbns import Isbns
from .testdata import TestData
from .assets import Assets

class Context(object):
    def __init__(self,
                 api_key,
                 host,
                 log = None,
                 validate_json = False,
                 requests_kwargs = None):
        self._api_key = api_key
        self._host = host
        if log:
            self._log = log.getChild('open_publishing')
        else:
            self._log = logging.getLogger('open_publishing')
        if not self._host.startswith("https://"):
            self._host = "https://" + self._host
        self._requests_kwargs = requests_kwargs if requests_kwargs else {} 
        self._gjp = GJP(self, validate_json)
        self._documents = Documents(self)
        self._users = Users(self)
        self._orders = Orders(self)
        self._order_fulfillments = OrderFulfillments(self)
        self._accounts = Accounts(self)
        self._events = Events(self)
        self._onix = Onix(self)
        self._imprints = Imprints(self)
        self._genres = Genres(self)
        self._isbns = Isbns(self)
        self._testdata = TestData(self)
        self._assets = Assets(self)
        self._brands = None
        self._territories = None
        self._me = None


    @property
    def api_key(self):
        return self._api_key

    @property
    def host(self):
        return self._host

    @property
    def log(self):
        return self._log

    @property
    def requests_kwargs(self):
        return self._requests_kwargs.copy()

    @property
    def gjp(self):
        return self._gjp

    @property
    def documents(self):
        return self._documents

    @property
    def users(self):
        return self._users

    @property
    def orders(self):
        return self._orders

    @property
    def order_fulfillments(self):
        return self._order_fulfillments

    @property
    def accounts(self):
        return self._accounts

    @property
    def events(self):
        return self._events

    @property
    def onix(self):
        return self._onix

    @property
    def imprints(self):
        return self._imprints

    @property
    def genres(self):
        return self._genres

    @property
    def isbns(self):
        return self._isbns

    @property
    def testdata(self):
        return self._testdata

    @property
    def assets(self):
        return self._assets

    @property
    def brands(self):
        if self._brands is None:
            self._brands = self._gjp.list_brands()
        return set(self._brands.values())

    @property
    def territories(self):
        if self._territories is None:
            countries = self._gjp.list_countries()
            self._territories = {country['code_iso_2'] for country in list(countries.values())} | {'WORLD'}
        return self._territories.copy()

    @property
    def me(self):
        if self._me is None:
            self._me = Me(self)
        return self._me
        
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.flush()
        self.gjp.session.close()

    def flush(self):
        self.documents.flush()
        self.users.flush()
        self.orders.flush()

            
            
