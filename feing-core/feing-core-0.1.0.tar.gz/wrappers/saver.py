# -*- coding: UTF-8 -*-
import os
from urllib import request

import requests

from wrappers.request import get_simple_header


class SaverBuilder(object):
    def __init__(self):
        self.headers = get_simple_header()

    @staticmethod
    def mkdir(folder):
        if os.path.exists(folder) is False:
            os.makedirs(folder)

    def save(self, url, folder=None, save_name=None, root_dir='download'):
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
            print('>>>下载完成:', save_name)
        except Exception as e:
            raise RuntimeError('>>>下载失败:', save_name, '\n错误:', str(e))

    def save_file(self, url, folder=None, save_name=None, headers=None, root_dir='download'):
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
            raise RuntimeError('>>>下载失败:', save_name, '\n错误:', str(e))

    @staticmethod
    def save_m3u8(url):
        # 提取ts视频的url
        url_array = url.split('/')
        prefix = '/'.join(url_array[:-1]) + '/'

        _temp_m3u8 = 'temp_m3u8.txt'
        try:
            m3u8_txt = requests.get(url, headers={'Connection': 'close'})

            with open(_temp_m3u8, 'wb') as file_input:
                file_input.write(m3u8_txt.content)

            urls = []

            m3u8_file = open(_temp_m3u8, 'rb')
            for line in m3u8_file.readlines():
                line_text = line.decode('utf-8')
                if '.ts' in line_text:
                    urls.append(prefix + line_text[:-1].strip('\n').replace('\r', ''))
                else:
                    continue

            m3u8_file.close()
            os.remove(_temp_m3u8)
            return urls
        except Exception as e:
            raise RuntimeError('>>>下载失败:', url, '\n错误:', str(e))
