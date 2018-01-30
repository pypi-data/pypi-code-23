from .context import Context as _Context
from .user import User
from .document import Document
from .order import Order
from .order_fulfillment import OrderFulfillment
from .prices import public as prices
from .catalog import public as catalog
from .taxes import public as tax

from .core.enums import DocumentStatus as status
from .core.enums import Gender as gender
from .core.enums import License as license
from .core.enums import PriceType as pricetype
from .core.enums import CatalogType as catalogtype
from .core.enums import TaxType as taxtype
from .core.enums import BookBinding as binding
from .core.enums import IsbnType as _isbn
from .core.enums import Subscription as subscription
from .core.enums import PublicationType as publication
from .core.enums import OnixStyle as _onixstyle
from .core.enums import OnixType as _onixtype
from .core.enums import OnixStatus as _onixstatus
from .core.enums import AdultFlag as adult_flag
from .core.enums import ChildrenFlag as children_flag
from .core.enums import AcademicCategory as academic_category

from .core.enums import Language as language
from .core.enums import VLBCategory as vlb_category
from .core.enums import Country as country
from .core.enums import ContributorRole as role
from .core.enums import BisacCode as bisac
from .core.enums import Currency as currency

from .core.enums import EBookFileType as _ebook_filetype
from .core.enums import PreviewFileType as _preview_filetype
from .core.enums import ContentType as _content_type
from .core.enums import FileType as _filetype

from .core.enums import EventTarget as _event_target
from .core.enums import EventAction as _event_action
from .core.enums import EventType as _event_type
from .core.enums import EventResult as _event_result

from .core.enums import ProvisionRuleAlgorithm as _provision_algorithm
from .core.enums import ProvisionRuleRole as _provision_role
from .core.enums import ProvisionChannelType as _provision_channel_type
from .core.enums import ProvisionChannelBase as _provision_channel_base

from .core.enums import UsersSearchType as users_search_type

from .core.enums import PreviewDisplayMode as _preview_display_mode
from .core.enums import PreviewTOCVisible as _preview_toc_visible

from .core.enums import ProfileShow as _profile_show

from .core.enums import AssetsCoverType as _assets_cover_type

from .core.enums import OrderItemType as _order_item_type
from .core.enums import ShippingType as _shipping_type
from .core.enums import ShippingStatus as _shipping_status
from .core.enums import ShippingLevel as _shipping_level

from .core.enums import ProcessingType as processing

from .assets import AssetNotReady, AssetExpired
from .gjp import ObjectNotFound, TemporaryNotAvailable, AssetCreationError

from .order import Address as _address
from .order import Person as _person

from .content import Content

class order(object):
    address = _address
    seller = _person
    buyer = _person
    class item(object):
        type = _order_item_type
    class shipping(object):
        type = _shipping_type
        status = _shipping_status
        level = _shipping_level

class isbn(object):
    class book(object):
        all = _isbn.book
    class ebook(object):
        all = _isbn.ebook
        epub = _isbn.epub
        pdf = _isbn.pdf
        mobi = _isbn.mobi

class files(object):
    ebook_filetype = _ebook_filetype
    preview_filetype = _preview_filetype
    content_type = _content_type
    filetype = _filetype

class assets(object):
    cover = _assets_cover_type

class events(object):
    target = _event_target
    action = _event_action
    type = _event_type
    result = _event_result

class onix(object):
    style = _onixstyle
    type = _onixtype
    status = _onixstatus
    
class provision(object):
    algorithm = _provision_algorithm
    role = _provision_role
    class channel(object):
        type = _provision_channel_type
        base = _provision_channel_base

class preview(object):
    display_mode = _preview_display_mode
    toc_visible = _preview_toc_visible

def context(api_key,
            host = "api.openpublishing.com",
            auth = None,
            timeout = 30,
            proxies = None,
            verify = None,
            cert = None,
            log = None,
            validate_json = False):
    request_kwargs = {}
    if auth is not None:
        request_kwargs['auth'] = auth
    if timeout is not None:
        request_kwargs['timeout'] = timeout
    if proxies is not None:
        request_kwargs['proxies'] = proxies
    if verify is not None:
        request_kwargs['verify'] = verify
    if cert is not None:
        request_kwargs['cert'] = cert
    return _Context(api_key, host, log, validate_json, request_kwargs)

class profile(object):
    show = _profile_show
