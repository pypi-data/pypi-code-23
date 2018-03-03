"""
Connections module is for handling variate connection types with one base class.
"""
# IMPORTANT: Import order is matter!
from .base import Base
from .httpclient import HTTPClient
from .oauthclient import OAuthClient
from .zookeeper import Zookeeper
