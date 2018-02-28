import logging

from brama.plugins import MiddlewarePlugin

logger = logging.getLogger(__name__)


@MiddlewarePlugin.register()
def rate_limiting(request):
    # rate_limits = request.route.get_config('rate_limits')
    return
