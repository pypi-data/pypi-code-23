from .req import SteamApiRequest
from .const import APP_ENDPOINT
from .language_code import LANGUAGE_CODE
import requests
from .. import error


def get_app_list():
    return SteamApiRequest.get(
        APP_ENDPOINT,
        '/GetAppList',
        'v2',
    )


def get_app_detail(appid, language, cc):
    payload = {
        'appids': appid,
        'cc': cc,
        'l': LANGUAGE_CODE[language],
    }

    response = requests.get('https://store.steampowered.com/api/appdetails', params=payload)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        error.handle_error(response)


def get_app_price(ids, cc):
    payload = {
        'appids': ','.join(str(i) for i in ids),
        'cc': cc,
        'filters': 'price_overview'
    }

    response = requests.get('https://store.steampowered.com/api/appdetails', params=payload)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        error.handle_error(response)