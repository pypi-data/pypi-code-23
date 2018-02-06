"""
Computer Science House OpenID Connect Backend for Python Social Auth
"""
from social-auth-core.backends.open_id_connect import OpenIdConnectAuth


class CSHAuth(OpenIdConnectAuth):
    name = 'csh'
    OIDC_ENDPOINT = 'https://sso.csh.rit.edu/auth/realms/csh'

