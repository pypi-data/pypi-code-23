# -*- coding: UTF-8 -*-
import os
from urllib import request

import requests


class OutPut(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/54.0.2840.100 Safari/537.36',
        }

    @staticmethod
    def mkdir(folder):
        if os.path.exists(folder) is False:
            os.makedirs(folder)

    def save_file(self, url, folder=None, save_name=None, root_dir='output'):
        save_dir = root_dir
        if save_name is None:
            save_name = url.split('/')[-1]
        if folder:
            print('>>>正在下载:', folder, '\n', url)
            save_dir = save_dir + os.path.sep + folder
        else:
            print('>>>正在下载:', save_name, '\n', url)

        self.mkdir(save_dir)
        save_file = save_dir + os.path.sep + save_name

        if os.path.exists(save_file):
            print('>>>本地已存在:', save_name, url)
            return
        try:
            request.urlretrieve(url, save_file)
            # content = html_download.Downloader().download(url)
            # with open(save_file, 'wb') as file_input:
            #     file_input.write(content)
            print('>>>下载完成:', save_name)
        except Exception as e:
            print('>>>下载失败:', save_name, '\n错误:', str(e))

    def save_session_file(self, url, folder=None, save_name=None, headers=None, root_dir='output'):
        save_dir = root_dir
        if save_name is None:
            save_name = url.split('/')[-1]
        if folder:
            print('>>>正在下载:', folder, '\n', url)
            save_dir = save_dir + os.path.sep + folder
        else:
            print('>>>正在下载:', save_name, '\n', url)

        self.mkdir(save_dir)
        save_file = save_dir + os.path.sep + save_name

        if os.path.exists(save_file):
            print('>>>本地已存在:', save_name, url)
            return
        try:
            if headers is None:
                headers = self.headers
            content = requests.get(url, headers=headers, timeout=60).content
            with open(save_file, 'wb') as file_input:
                file_input.write(content)
            print('>>>下载完成:', save_name)
        except Exception as e:
            print('>>>下载失败:', save_name, '\n错误:', str(e))
