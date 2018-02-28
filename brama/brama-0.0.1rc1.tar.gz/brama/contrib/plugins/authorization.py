import logging
from inspect import isawaitable

from sanic.response import json

from brama.plugins import MiddlewarePlugin, AuthorizationPlugin

logger = logging.getLogger(__name__)


async def get_auth_value(request, plugin):
    try:
        result = plugin.get_authorization_value(request)
        if isawaitable(result):
            result = await result
        return result
    except NotImplementedError:
        pass

    # Take from Authorization header by default
    header_name = request.app.config['BRAMA_AUTHORIZATION_HEADER']
    return request.headers.get(header_name.lower())


@MiddlewarePlugin.register()
async def authorization(request):
    request.authorization = None

    _config = request.route.get_config('authorization')
    if not _config:
        # No authorization configured for this endpoint.
        return

    if not isinstance(_config, list):
        auth_plugins = [_config]
    else:
        auth_plugins = _config

    for plugin_ in auth_plugins:
        if isinstance(plugin_, str):
            plugin = request.app.plugins_registry.get(plugin_)
        else:
            plugin = plugin_

        if plugin_ and plugin is None:
            raise ValueError('Can not find plugin {}'.format(plugin_))

        if not isinstance(plugin, AuthorizationPlugin):
            err = 'Expect <AuthorizationPlugin>, got {} instead'.format(plugin)
            raise TypeError(err)

        auth_value = await get_auth_value(request, plugin)
        try:
            authorization = plugin.process_authorization_value(request.app,
                                                               auth_value)
            if isawaitable(authorization):
                authorization = await authorization

        except NotImplementedError:
            authorization = None

        if authorization is not None:
            request.authorization = authorization
            break

    if not request.authorization:
        return json({}, status=401)
