from .http import post
from urllib.parse import urlencode


def generate_auth_endpoint(
    client_id: str,
    scope: str = None,
) -> str:
    """
    Generate authentication url that is used to redirect the user to the
    github login page.
    """
    auth_request_url = 'https://github.com/login/oauth/authorize'

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
    }

    return auth_request_url + '?' + urlencode(params)


async def get_access_token(
    session_code: str,
    client_id: str,
    client_secret: str,
) -> str:
    """
    This sends a post request to the github API. If credentials are correct,
    we return an access_token. This token can be used to make authenticated
    requests to the github API for a certain user.
    """
    access_token_request_url = 'https://github.com/login/oauth/access_token'

    headers = {
        'content-type': 'application/json',
        'Accept': 'application/json',
    }

    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': session_code
    }

    result = await post(
        url=access_token_request_url,
        json=payload,
        headers=headers,
        return_type='json',
    )

    return result.get('access_token')
