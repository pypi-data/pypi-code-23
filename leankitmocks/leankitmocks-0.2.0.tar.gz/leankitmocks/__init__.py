from json import load
from re import search
from os import path
from os import listdir
from warnings import warn

import leankit
from leankit import *


__version__ = "0.2.0"


class Mock():
    _versions_ = {}
    _folder_ = path.join(path.dirname(path.realpath(__file__)), 'data')

    def get(self, url):
        log.debug(f'GET {url}')
        url = url.lower()
        if 'getcard' in url:
            return self._get_card_(url)
        elif 'history' in url:
            return self._get_history_(url)
        elif 'boardversion' in url:
            return self._get_newer_if_exists_(url)
        elif 'archive' in url:
            return self._get_archive_(url)
        else:
            return self._load_response_(url)

    def _get_newer_if_exists_(self, url):
        endpoint = '/board/(\d{9})/boardversion/(\d+)/getnewerifexists'
        board_id, version = self._get_ids_(endpoint, url)
        dirname = path.join(self._folder_, 'board', board_id, 'boardversion')
        folders = listdir(dirname)
        try:
            available = int(folders[0] if folders else 0)
        except ValueError:
            warn(f'Invalid folder name at {dirname}')
            return None
        if available > int(version):
            self._versions_[board_id] = available
            url = url.replace(f'/{version}/', f'/{available}/')
            return self._load_response_(url)

    def _get_card_(self, url):
        return self._get_new_('/board/(\d{9})/getcard/(\d{9})', url)

    def _get_history_(self, url):
        return self._get_new_('/card/history/(\d{9})/(\d{9})', url)

    def _get_archive_(self, url):
        board_id = self._get_ids_('/board/(\d{9})/archive', url)[0]
        if board_id in self._versions_:
            version = self._versions_[board_id]
            url = url.replace('/archive', f'/{version}/archive')
        return self._load_response_(url)

    def _get_new_(self, endpoint, url):
        board_id, card_id = self._get_ids_(endpoint, url)
        if board_id in self._versions_:
            url = url.replace(card_id, f'{self._versions_[board_id]}/{card_id}')
        return self._load_response_(url)

    def _get_ids_(self, endpoint, url):
        matches = search(endpoint, url)
        if matches:
            return matches.groups()
        else:
            raise ConnectionError('Server responded with code 404')

    def _load_response_(self, url):
        try:
            filename = path.join(self._folder_, url.strip('/') + '.json')
            with open(filename) as data:
                return load(data)
        except FileNotFoundError:
            raise ConnectionError('Server responded with code 404')


leankit.api = leankit.kanban.api = Mock()
