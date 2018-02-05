# -*- coding: UTF-8 -*-
import os
from contextlib import closing

import requests


class Downloader(object):
    def __init__(self, url, filename, save_root_dir='output'):
        self.url = url
        self.filename = filename
        self.save_root_dir = save_root_dir

    def download(self):
        print('*' * 100)
        print('\t\t\t\t\t\t\t\t欢迎使用文件下载小助手')
        print('*' * 100)
        with closing(requests.get(self.url, stream=True)) as response:
            chunk_size = 1024
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                print('文件大小:%0.2f KB' % (content_size / chunk_size))
                progress = ProgressBar("%s下载进度" % self.filename,
                                       total=content_size,
                                       unit="KB",
                                       chunk_size=chunk_size,
                                       run_status="正在下载",
                                       fin_status="下载完成")

                save_dir = self.save_root_dir
                if os.path.exists(save_dir) is False:
                    os.makedirs(save_dir)
                save_file = save_dir + os.path.sep + filename

                if os.path.exists(save_file):
                    print('>>>本地已存在:', filename, url)
                    return
                with open(save_file, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))
            else:
                print('链接异常:%s' % url)


class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0,
                 unit='', sep='/', chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # [名称] 状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status, self.count / self.chunk_size,
                             self.unit, self.seq, self.total / self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)


if __name__ == '__main__':
    url = 'http://www.demongan.com/source/20170510/ccc/%E6%91%84%E5%83%8F%E5%A4%B4%E5%B7%A5%E5%85%B7.zip'
    filename = '摄像头记录工具.zip'
    # url = input('请输入需要下载的文件链接:\n')
    # filename = url.split('/')[-1]
    Downloader(url, filename).download()
