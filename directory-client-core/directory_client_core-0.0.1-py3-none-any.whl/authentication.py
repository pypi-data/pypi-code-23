import abc


class BaseAuthenticator(abc.ABC):
    header_name = 'Authorization'
    header_template = abc.abstractproperty()
    value = None

    def __init__(self, value):
        self.value = value

    def get_auth_headers(self):
        return {
            self.header_name: self.header_template.format(self.value)
        }


class BearerAuthenticator(BaseAuthenticator):
    header_template = 'Bearer {}'


class SessionSSOAuthenticator(BaseAuthenticator):
    header_template = 'SSO_SESSION_ID {}'


class AuthenticatorNegotiator:
    def __new__(self, bearer_token, sso_session_id):
        assert bearer_token or sso_session_id
        if bearer_token:
            return BearerAuthenticator(bearer_token)
        elif sso_session_id:
            return SessionSSOAuthenticator(sso_session_id)
