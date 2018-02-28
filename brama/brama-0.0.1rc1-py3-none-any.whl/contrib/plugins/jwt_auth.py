import logging
from inspect import isawaitable

import jwt
from sanic.response import json, BaseHTTPResponse

from brama.plugins import AuthorizationFlowPlugin, AuthorizationPlugin
from brama.utils import pathjoin

logger = logging.getLogger(__name__)


@AuthorizationPlugin.register()
class JWTToken(object):
    HEADER_PREFIX = None

    @classmethod
    def _auth_type(cls, app):
        return cls.HEADER_PREFIX or app.config.get('BRAMA_JWT_HEADER_PREFIX')

    @classmethod
    def process_authorization_value(cls, app, value):
        try:
            auth_type, auth_value = value.split(None, 1)
        except (ValueError, AttributeError):
            return
        if auth_type.upper() != cls._auth_type(app).upper():
            return

        payload = cls._decode_token(auth_value, app.config)
        return payload

    @classmethod
    def _decode_token(cls, token, config):
        try:
            payload = jwt.decode(token, config.BRAMA_SECRET_KEY,
                                 algorithm=config.BRAMA_JWT_ALGORITHM)
        except (jwt.exceptions.DecodeError):
            return

        return payload


@AuthorizationFlowPlugin.register()
class jwt_auth(object):

    def process_login(self, request, username, password):
        raise NotImplementedError()

    async def login_handler(self, request):
        app = request.app
        config = app.config
        data = request.json
        try:
            username, password = data['username'], data['password']
        except KeyError:
            return json({'error': 'Invalid data'}, status=400)

        login_plugins = app.enabled_plugins(required_methods=['process_login'])
        result = None
        for plugin in login_plugins:
            try:
                result = plugin.process_login(request, username, password)
                if isawaitable(result):
                    result = await result
            except NotImplementedError:
                continue
            if result:
                break

        if isinstance(result, BaseHTTPResponse):
            return result

        if not result:
            return json({'error': 'Can not authenticate'}, status=401)

        # TODO: https://goo.gl/jpYvwk
        payload = {'some': 'payload'}
        payload.update(result)
        token = jwt.encode(payload, config.BRAMA_SECRET_KEY,
                           algorithm=config.BRAMA_JWT_ALGORITHM)
        return json({'access_token': token})

    def verify_token_handler(self, request):
        config = request.app.config
        token = request.original_request.json.get('access_token')
        if not token:
            return json({'error': 'Invalid params'}, status=400)
        return json({
            'is_valid': bool(self._decode_token(token, config)),
        })

    def revoke_token_handler(self, request):
        return

    def get_extra_routes(self, app):
        path_prefix = app.config.BRAMA_AUTH_PATH
        return [
            {
                'url_path': pathjoin(path_prefix, 'login'),
                'name': 'JWTLogin',
                'handler': self.login_handler,
                'methods': ['POST'],
                'stream': False,
                'authorization': [],
            },
            {
                'url_path': pathjoin(path_prefix, 'verify_token'),
                'name': 'JWTVerify',
                'handler': self.verify_token_handler,
                'methods': ['POST'],
                'stream': False,
                'authorization': [],
            },
            {
                'url_path': pathjoin(path_prefix, 'revoke_token'),
                'name': 'JWTRevoke',
                'handler': self.revoke_token_handler,
                'methods': ['POST'],
                'stream': False,
                'authorization': [],
            },
        ]
