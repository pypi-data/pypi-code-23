# -*- coding: UTF-8 -*-
import os
from contextlib import closing

import requests
from tqdm import tqdm

from wrappers.request import get_simple_header


class DownloadBuilder(object):
    def __init__(self):
        self.headers = get_simple_header()

    def download(self, url, headers=None, filename=None, output='download'):
        if headers is None:
            headers = self.headers
        if filename is None:
            filename = url.split('/')[-1]
        with closing(requests.get(url, headers=headers, stream=True)) as response:
            content_size = int(response.headers['content-length'])
            chunk_size = 1000
            file_size = content_size / chunk_size ** 2  # KB
            if response.status_code == 200:
                save_dir = output
                if os.path.exists(save_dir) is False:
                    os.makedirs(save_dir)
                save_file = save_dir + os.path.sep + filename

                if os.path.exists(save_file):
                    print('>>>本地已存在:', filename, url)
                    return
                try:
                    process_bar = tqdm(total=content_size, unit='B', unit_scale=True, miniters=1,
                                       desc='[%s - %0.2f M]' % (filename, file_size))
                    with open(save_file, "wb") as file:
                        for data in response.iter_content(chunk_size=chunk_size):
                            file.write(data)
                            process_bar.update(len(data))
                    process_bar.close()
                except Exception as e:
                    os.remove(save_file)
                    raise RuntimeError('服务器错误：%s' % str(e))
            else:
                raise RuntimeError('链接异常：%s' % url)
        print('[%s]：下载完成' % filename)


def main():
    url = 'http://www.demongan.com/source/20170510/ccc/%E6%91%84%E5%83%8F%E5%A4%B4%E5%B7%A5%E5%85%B7.zip'
    filename = '摄像头记录工具.zip'
    # url = input('请输入需要下载的文件链接:\n')
    # filename = url.split('/')[-1]
    DownloadBuilder().download(url=url, filename=filename)


if __name__ == '__main__':
    main()
