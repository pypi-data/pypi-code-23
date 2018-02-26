"""
Atmosphere service compute.
"""
from threepio import logger

from giji_rtwo import settings

from giji_rtwo.provider import AWSProvider, EucaProvider, OSProvider
from giji_rtwo.driver import EucaDriver, AWSDriver

from libcloud.common.types import InvalidCredsError


OSProvider.set_meta()

