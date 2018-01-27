from .api.app import *
from .error import SteamAPIFailureNotFound


class App(object):
    """
    Steam App Service
    """

    def __init__(self):
        pass

    @staticmethod
    def list():
        """
        Gets the complete list of public apps.

        Sample

        .. code-block:: javascript

            [{
                "appid": 5,
                "name": "Dedicated Server"
            },
            {
                "appid": 7,
                "name": "Steam Client"
            },
            {
                "appid": 8,
                "name": "winui2"
            }]

        :return: list(dict)
        """
        res = get_app_list()
        app_list = res['applist']

        return app_list['apps']

    @staticmethod
    def detail(id, language='zh-cn', cc='cn'):
        """
        Get the detail of an app with id and locale
    
        :param id: steam app id
        :param language: language code. e.g. 'zh-cn', 'zh-tw', 'en', 'ja', 'ko'
        :param cc: country code set for currency. e.g. 'cn'

        Sample

        .. code-block:: javascript
    
            {
                "type": "game",
                "name": "xxxxx",
                "steam_appid": 192929
                ...
            }
    
        :retutn: dict
        """
        res = get_app_detail(id, language, cc)
        data = res[str(id)]
        if data['success'] is True:
            return data['data']
        else:
            raise SteamAPIFailureNotFound


class Price(object):
    def __init__(self):
        pass

    @staticmethod
    def list(ids, cc='cn'):
        res = get_app_price(ids, cc)
        return res

