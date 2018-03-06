import json
import re
import requests
import time


class AlAudio(object):
    _api_url = 'https://vk.com/al_audio.php'
    _cookies = None
    _uid = None
    _user_agent = '%s %s %s %s' % (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/60.0.3112.101',
        'Safari/537.36'
    )
    _playlist = None
    _playlist_id = -1  # Default - all tracks
    _sleep_time = 1
    _split_audio_size = 5

    def _load_data(self, offset=0):
        return {
            'access_hash': '',
            'act': 'load_section',
            'al': 1,
            'claim': '0',
            'offset': offset,
            'owner_id': self._uid,
            'playlist_id': self._playlist_id,
            'type': 'playlist'
        }

    @property
    def _headers(self):
        return {
            'User-Agent': self._user_agent,
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    def __init__(self, uid, cookies):
        self._uid = uid
        self._cookies = cookies
        self._playlist = []

    def main(self):
        self._fill_playlist()
        return self._parse_playlist()

    def set_playlist_id(self, _id):
        self._playlist_id = _id

    def _fill_playlist(self, offset=0):
        response = self._parse_response(self._post(
            self._api_url,
            self._load_data(offset)
        ))
        if response.get('type', '') != 'playlist':
            return
        self._playlist += response.get('list', [])
        if int(response.get('hasMore', 0)) != 0:
            time.sleep(self._sleep_time)  # sleeping. anti-bot
            self._fill_playlist(response.get('nextOffset'))

    def _post(self, url, data):
        response = requests.post(
            url, data=data,
            headers=self._headers,
            cookies=self._cookies
        )
        for i in response.cookies:
            self._cookies[i] = response.cookies[i]
        return response.text

    @staticmethod
    def _parse_response(response, default=None):
        if default is None:
            default = {}
        try:
            data = re.search(r'<!json>(.+?)<!>', response).group(1)
            return json.loads(data)
        except Exception:
            return default

    def _parse_playlist(self):
        official_parse = []
        response = []
        for i in self._playlist:
            if i[2] == '':
                official_parse.append(i)
            else:
                response.append((i[2], i[3], i[4]))
            if len(official_parse) > self._split_audio_size:
                time.sleep(self._sleep_time / 20)
                response += self._parse_list_items(official_parse)
                official_parse = []
        return response

    def _parse_list_items(self, items):
        result = []
        for item in items:
            result.append('%d_%d' % (item[1], item[0]))
        return self._decode_playlist(result)

    @staticmethod
    def _get_reload_data(ids):
        return {
            'act': 'reload_audio',
            'al': 1,
            'ids': ','.join(ids)
        }

    def _decode_playlist(self, items):
        data = self._post(
            self._api_url,
            self._get_reload_data(items)
        )
        return self._rebuild_response(data)

    def _rebuild_response(self, response):
        data = self._parse_response(response)
        if isinstance(data, list):
            return [(i[2], i[3], i[4]) for i in data]
        return []
