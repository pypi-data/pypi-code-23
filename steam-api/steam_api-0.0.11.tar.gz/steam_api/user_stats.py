# -*- coding: utf-8 -*-

from .api.user_stats import get_global_achievements_for_app, \
    get_number_of_current_player, \
    get_schema_for_game, \
    get_global_stats_for_game
from .error import ParameterRequiredError, ParameterNotInEnumError


class GameUserStats(object):
    """
    Game User Stats Service

    .. note::
       get global user stats of game

    Example 1:

    .. code-block:: python

       # initialize class with game_id=400
       user_stats = steam_api.user_stats.GameUserStats(440)

       # get glocal achievements percentages of this game
       user_stats.global_achievements_percentages

    Example 2:

    .. code-block:: python

       from steam_api.error import ParameterRequiredError

       # initialize class without game_id
       try:
         steam_api.user_stats.GameUserStats()
       except: ParameterRequiredError
         # catch error
    """

    def __init__(self, game_id=None):
        """
        init

        :param int game_id: game id
        :raises ParameterRequiredError: if `game_id` is not provided
        """
        if game_id is None:
            raise ParameterRequiredError('game id can not be empty')

        #: game id
        self.game_id = game_id

    @property
    def global_achievements_percentages(self):
        """
        global achievements percentages

        Sample

        .. code-block:: javascript

           [{
                "name": "a0",
                "percent": 52.536167144775391
            },
            {
                "name": "24",
                "percent": 46.570213317871094
            },
            {
                "name": "1",
                "percent": 45.045833587646484
            },
            {
                "name": "18",
                "percent": 42.387386322021484
            }]

        :return: list(dict)
        """

        res = get_global_achievements_for_app(self.game_id)
        achievements = res['achievementpercentages']

        return achievements['achievements']

    # TODO
    def global_stats_of_achievements(self, name=[], count=20):
        """
        global stats of achievements defined in Steamworks

        Example:
        http://api.steampowered.com/ISteamUserStats/GetGlobalStatsForGame/v0001/?appid=17740&count=1&name[0]=global.map.emp_isle

        :param name: Name of the achievement as defined in Steamworks.
        :type name: list(str)
        :param int count: Length of the array of global stat names you will be passing.

        :return: {}
        """

        res = get_global_stats_for_game(self.game_id, count, name)
        return res['response']

    @property
    def number_of_current_player(self):
        """
        current players

        Sample

        .. code-block:: javascript

           {
             "player_count": 312,
             "result": 1
           }

        :return: dict
        """
        res = get_number_of_current_player(self.game_id)
        players = res['response']
        return players

    def schema(self, key, language):
        """
        GetSchemaForGame returns gamename, gameversion and availablegamestats(achievements and stats).

        :param str key: web api key
        :param language: Language. If specified, it will return language data for the requested language.
        :return: {}
        :raises ParameterNotInEnumError: if the `language` is not supported


        Return Sample

        .. code-block:: javascript

            {
            "achievements": [
                {
                    "name": "LILAC",
                    "defaultvalue": 0,
                    "displayName": "丁香與醋栗",
                    "hidden": 1,
                    "icon": "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/292030/60785871894
                         83353f06f48d0eefdaaa0791e9e13.jpg",
                    "icongray": "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/292030/8246
                           dc3a496e13c058572dab37099e76a6cd0b77.jpg"
                },
                {
                    "name": "FRIEND_IN_NEED",
                    "defaultvalue": 0,
                    "displayName": "伸出援手",
                    "hidden": 1,
                    "icon": "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/
                           292030/07bae88f1ee9b856ddfc1d8e28ae7eedd4bcde95.jpg",
                    "icongray": "http://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/
                            292030/cea97617b65ab7d42f37cbb9a77c7290775c789a.jpg"
                }],
            "stats": [
                {
                    "name": "sc_hr",
                    "defaultvalue": 0,
                    "displayName": "horse_riding"
                },
                {
                    "name": "sc_slng",
                    "defaultvalue": 0,
                    "displayName": "sailing"
                },
            ]
            }

        Example 1

        .. code-block:: python

           from steam_api.game_stats import GameUserStats

           # get list with language option which is Enum
           game_stats.schema(STEAM_WEB_API_KEY, 'zh-cn')


        Example 2

        .. code-block:: python

           from steam_api.game_stats import GameUserStats
           from steam_api.error import ParameterNotInEnumError

           game_stats = GameUserStats(440)

           try:
               game_stats.schema(YOUR_STEAM_WEB_API_KEY, 'non-exist-language-code')
           except ParameterNotInEnumError:
              #catch error

        """
        res = get_schema_for_game(key=key, app_id=self.game_id, language=language)
        game = res['game']
        return game['availableGameStats']
