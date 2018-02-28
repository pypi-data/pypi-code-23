import falcon
import jwt

def _default_failed(exception):
    raise falcon.HTTPUnauthorized()


class ConfigurationError(Exception):
    pass


class ParseJWTMiddleware:
    """Strip a JWT from a cookie or a header

    Example:
        import falcon
        from falcon_helpers.middlewares.parsejwt import ParseJWTMiddleware

        api = falcon.API(
            middleware=[
                ParseJWTMiddleware(
                    audience='your-audience',
                    secret='a-really-great-random-string',
                    cookie_name='MyCookieName')
            ]
        )

    Attributes:
        audience: (string) A string audience which is passed to the JWT decoder

        secret: (string) A secret key to verify the token

        pubkey: (string) When using RS256, pass a public key not a token

        when_fails: (function) A function to execute when the authentication
            fails

        cookie_name: (string) the name of the cookie to look for

        header_name: (string) the name of the cookie to look for

        context_key: (string) the key to put the JWT

    """

    def __init__(self, audience, secret=None, pubkey=None,
                 cookie_name=None, header_name=None,
                 context_key='auth_token_contents',
                 when_fails=_default_failed):

        if cookie_name and header_name:
            raise ConfigurationError('Can\'t pull the token from both a header'
                                     ' and a cookie')

        if not cookie_name and not header_name:
            cookie_name = 'X-AuthToken'

        self.audience = audience
        self.secret = secret
        self.pubkey = pubkey
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.failed_action = when_fails

        if (self.pubkey is not None
            and not self.pubkey.startswith('ssh-rsa')):
            raise ConfigurationError(
                'A public key for RS256 encoding must be in PEM Format')

    def verify_request(self, token):
        if not token:
            raise ValueError('No token found')

        header = jwt.get_unverified_header(token)

        (type_, verify_with) = (('public key', self.pubkey)
                                if header['alg'] == 'RS256'
                                else ('secret key', self.secret))

        if verify_with is None:
            raise ConfigurationError('You must pass the correct verification'
                                     f' type for this algorithm.'
                                     f' {header["alg"]} requires a {type_}.')

        return jwt.decode(token, verify_with, audience=self.audience)


    def process_request(self, req, resp):
        token = req.cookies.get(self.cookie_name, False)

        try:
            req.context['auth_token_contents'] = self.verify_request(token)
        except Exception as e:
            return self.failed_action(e, req, resp)
