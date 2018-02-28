import falcon


def _default_failed(req, resp, **kwargs):
    raise falcon.HTTPFound('/auth/login')


class AuthRequiredMiddleware:
    """Requires a cookie be set with a valid JWT or fails

    Example:
        import falcon
        from falcon_helpers.middlewares.auth_required import AuthRequiredMiddleware

        class Resource:
            auth_required = True

            def on_get(self, req, resp):
                # ...

        def when_fails_auth(req, resp, token_value):
            raise TerribleException(token_value)

        api = falcon.API(
            middleware=[
                AuthRequiredMiddleware(when_fails=when_fails_auth)
            ]
        )

        api.add_route('/', Resource())

    Attributes:
        resource_param: The paramater to pull the boolean from

        context_key: the key the token will be found on the request

        when_fails: (function) A function to execute when the authentication
            fails
    """

    def __init__(self, resource_param='auth_required',
                 context_key='auth_token_contents',
                 when_fails=_default_failed):

        self.resource_param = resource_param
        self.context_key = context_key
        self.failed_action = when_fails

    def process_resource(self, req, resp, resource, params):
        required = getattr(resource, self.resource_param, True)
        token_value = req.context.get(self.context_key, None)

        token_value = None if isinstance(token_value, Exception) else token_value

        if required and not token_value:
            return self.failed_action(req=req, resp=resp, token_value=token_value)
