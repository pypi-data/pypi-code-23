import logging
from .web import BGWeb
from .server import BGServer
logging.getLogger('bgweb').addHandler(logging.NullHandler())