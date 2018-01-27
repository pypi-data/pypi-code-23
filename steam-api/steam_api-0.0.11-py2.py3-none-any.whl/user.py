# -*- coding: utf-8 -*-

from .api.user import *
from future.utils import python_2_unicode_compatible
from .error import ParameterNotInEnumError, ParameterRequiredError


@python_2_unicode_compatible
class User(object):
    """
    User Service
    """

    def __init__(self, key=None, steam_id=None):
        """
        init user class

        :param key: web api key
        :type key: str or None
        :param str steam_id: steam id
        :raises ParameterRequiredError: if `steam_id` or `key` is not provided
        """

        if key is None:
            raise ParameterRequiredError('key can not be empty')

        if steam_id is None:
            raise ParameterRequiredError('steam_id can not be empty')

        #: api key
        self.key = key

        #: 64 bit steam id
        self.steam_id = steam_id

    def __str__(self):
        return '<Steam User with id: {id}>'.format(id=self.steam_id)

    @property
    def profile(self):
        """
        user's profile

        Sample

        .. code-block:: javascript

              {
                "steamid": "76561197960435531",
                "communityvisibilitystate": 3,
                "profilestate": 1,
                "personaname": "John doe",
                "lastlogoff": 1482730903,
                "profileurl": "http://steamcommunity.com/profiles/76561197960435531/",
                "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb.jpg",
                "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg",
                "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
                "personastate": 0,
                "primaryclanid": "103582791429521408",
                "timecreated": 1063406959,
                "personastateflags": 0
            }

        :return: dict()
        """

        res = get_player_summaries(self.key, self.steam_id)
        profile = res['response']
        return profile['players'][0]

    def profiles(self, steam_id_list=None):
        """
        multi users profile

        :param steam_id_list: list of steam ids, e.g. ['1', '3', '2']
        :type steam_id_list: list(str)
        :return: list(dict)

        Sample

        .. code-block:: javascript

            [
              {
                "steamid": "76561197960435531",
                "communityvisibilitystate": 3,
                "profilestate": 1,
                "personaname": "John doe",
                "lastlogoff": 1482730903,
                "profileurl": "http://steamcommunity.com/profiles/76561197960435531/",
                "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb.jpg",
                "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_medium.jpg",
                "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/fe/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
                "personastate": 0,
                "primaryclanid": "103582791429521408",
                "timecreated": 1063406959,
                "personastateflags": 0
              },
              {
                "steamid": "76561197960435530",
                "communityvisibilitystate": 3,
                "profilestate": 1,
                "personaname": "Robin",
                "lastlogoff": 1510438836,
                "profileurl": "http://steamcommunity.com/id/robinwalker/",
                "avatar": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4.jpg",
                "avatarmedium": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4_medium.jpg",
                "avatarfull": "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4_full.jpg",
                "personastate": 0,
                "realname": "Robin Walker",
                "primaryclanid": "103582791429521412",
                "timecreated": 1063407589,
                "personastateflags": 0,
                "loccountrycode": "US",
                "locstatecode": "WA",
                "loccityid": 3961
              }
            ]

        """
        if type(steam_id_list) is 'list':
            user_id = ','.join(steam_id_list)
        else:
            user_id = self.steam_id

        res = get_player_summaries(self.key, user_id)
        profiles = res['response']
        return profiles['players']

    def friends(self, relationship='all'):
        """
        get friends list

        :param str relationship: Enum, `all` or `friend`
        :return: list(dict)


        Sample

        .. code-block:: javascript

            [
            {
                "steamid": "76561197960265731",
                "relationship": "friend",
                "friend_since": 0
            },
            {
                "steamid": "76561197960265738",
                "relationship": "friend",
                "friend_since": 0
            },
            {
                "steamid": "76561197960265740",
                "relationship": "friend",
                "friend_since": 0
            }]
        """

        res = get_friend_list(self.key, self.steam_id, relationship)
        friends = res['friendslist']
        return friends['friends']

    def game_achievements(self, app_id=None, language=''):
        """
        get user's achievements of this game

        :param int app_id: app id
        :param str language: Enum, actually
        :return: dict

        Sample

        .. code-block:: javascript

            {
            "steamID": "76561197960435530",
            "gameName": "Sid Meier's Civilization VI",
            "achievements": [
              {
                "apiname": "NEW_ACHIEVEMENT_2_0",
                "achieved": 0,
                "unlocktime": 0,
                "name": "遊戲、開拓者、比賽",
                "description": "贏得一場開拓者難度或更難的常規比賽"
              },
              {
                "apiname": "NEW_ACHIEVEMENT_2_1",
                "achieved": 0,
                "unlocktime": 0,
                "name": "愛爾蘭的心跳",
                "description": "贏得一場首領難度或更難的常規比賽"
              },
              {
                "apiname": "DLC6_ACHIEVEMENT_10",
                "achieved": 0,
                "unlocktime": 0,
                "name": "有聽說過上帝嗎？",
                "description": "在「涅槃之路」情景中改變3座敵對聖城的信仰"
              }
            ],
            "success": true
            }
        """

        res = get_player_achievements(self.key, self.steam_id, app_id, language)
        return res['playerstats']

    def game_stats(self, app_id=None, language=''):
        """
        get user's stats of this game

        :param int app_id: app id
        :param str language: Enum, actually
        :return: dict

        Sample

        .. code-block:: javascript

             {
              "steamID": "76561197960435530",
              "gameName": "",
              "achievements": [
                {
                  "name": "LILAC",
                  "achieved": 1
                },
                {
                  "name": "FRIEND_IN_NEED",
                  "achieved": 1
                },
                {
                  "name": "NECROMANCER",
                  "achieved": 1
                },
              ],
             "stats": [
                {
                  "name": "sc_hr",
                  "value": 65
                },
                {
                  "name": "sc_slng",
                  "value": 5
                },
                {
                  "name": "sc_at",
                  "value": 34
                }
              ]
             }
        """
        res = get_user_stats_for_game(self.key, self.steam_id, app_id, language)
        return res['playerstats']

    def owned_games(self, include_appinfo=True,
                    include_played_free_games=True, appids_filter=[]):
        """
        get owned game list

        :param bool include_appinfo: as said
        :param bool include_played_free_games: as said
        :param list appids_filter: filter
        :return: dict

        Sample

        .. code-block:: javascript

            {
            "game_count": 812,
            "games": [
              {
                "appid": 10,
                "playtime_forever": 32
              },
              {
                "appid": 20,
                "playtime_forever": 0
              },
              {
                "appid": 30,
                "playtime_forever": 0
              },
            ]
            }
        """

        res = get_owned_game(self.key, self.steam_id,
                             include_appinfo, include_played_free_games, appids_filter)
        return res['response']

    def recently_played_games(self, limit=1):
        """
        get recently played games list

        :param int limit: list size
        :return: list

        Sample

        .. code-block:: javascript

            {
            "total_count": 2,
            "games": [
            {
                "appid": 411300,
                "name": "ELEX",
                "playtime_2weeks": 3010,
                "playtime_forever": 5111,
                "img_icon_url": "695b3033fd72bcc3d85d02da2dbe719bd9856fc3",
                "img_logo_url": "150e18124d7b28493019dc3e14983aea6d731b59"
            },
            {
                "appid": 435150,
                "name": "Divinity: Original Sin 2",
                "playtime_2weeks": 610,
                "playtime_forever": 1874,
                "img_icon_url": "519a99caef7c5e2b4625c8c2fa0620fb66a752f3",
                "img_logo_url": "a83a75b8338e5576bea30f9f52c4eb2454e18efd"
            }]
            }
        """

        res = get_recently_played_games(self.key, self.steam_id, limit)
        return res['response']

    @property
    def badges(self):
        """
        get badges

        :return: dict

        Sample

        .. code-block:: javascript

            {
              "badges": [
              {
                "badgeid": 13,
                "level": 612,
                "completion_time": 1510442789,
                "xp": 862,
                "scarcity": 190839
              },
              {
                "badgeid": 2,
                "level": 2,
                "completion_time": 1447118256,
                "xp": 200,
                "scarcity": 9242789
              }],
              "player_xp": 3662,
              "player_level": 22,
              "player_xp_needed_to_level_up": 238,
              "player_xp_needed_current_level": 3600
            }
        """

        res = get_badges(self.key, self.steam_id)
        return res['response']

    @property
    def steam_level(self):
        """
        get steam level

        :return: dict

        Sample

        .. code-block:: javascript

            {
              "player_level": 22
            }
        """

        res = get_steam_level(self.key, self.steam_id)
        return res['response']

    @property
    def groups(self):
        """
        get groups

        :return: dict

        Sample

        .. code-block:: javascript

            {
            "success": true,
            "groups": [
              {
                "gid": "4"
              },
              {
                "gid": "70"
              },
              {
                "gid": "88"
              }
            ]
            }
        """

        res = get_user_group_list(self.key, self.steam_id)
        return res['response']

    # TODO
    @property
    def is_playing_shared_game(self):
        """
        is playing shared game or not

        :return:
        """
        pass

    # TODO
    @property
    def bans(self):
        # handle multi users input
        """
        get banned list

        :return:
        """

        res = get_player_bans(self.key, self.steam_id)
        return res['response']

