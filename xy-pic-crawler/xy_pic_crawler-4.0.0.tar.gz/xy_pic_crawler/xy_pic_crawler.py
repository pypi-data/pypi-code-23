import os
import re
import urllib
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
import time
import xy_picporn

timeout = 5
socket.setdefaulttimeout(timeout)


class Crawler:
    __time_sleep = 0.1
    __counter = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    def __init__(self, t=0.1):
        self.time_sleep = t

    def __save_image(self, rsp_data, word):
        dir_path = './' + word
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        self.__counter = len(os.listdir(dir_path)) + 1
        for image_info in rsp_data['imgs']:
            try:
                time.sleep(self.time_sleep)
                fix = self.__get_suffix(image_info['objURL'])
                res_path = dir_path + '/' + str(self.__counter) + str(fix)
                urllib.request.urlretrieve(image_info['objURL'], res_path)
            except urllib.error.HTTPError as urllib_err:
                continue
            except Exception as err:
                time.sleep(1)
                # print(err)
                # print("产生未知错误，放弃保存")
                continue
            else:
                print("图片+1,已有" + str(self.__counter) + "张图片")
                self.__counter += 1

        self.__check_imageporn(dir_path)

        return
    def __check_imageporn(self,dirpath):
        print(dirpath)
        print('开始性感图片检测,请稍等片刻...')
        files = os.listdir(dirpath)
        i = 1
        for filename in files:
            if xy_picporn.pic_porn(dirpath+'/'+filename) :
                os.remove(dirpath+'/'+filename)
                i+=1

        print('发现'+str(i)+'张性感图片，嘻嘻，已删除~~~')

    # 获取后缀名
    @staticmethod
    def __get_suffix(name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpeg'

    # 获取前缀
    @staticmethod
    def __get_prefix(name):
        return name[:name.find('.')]

    # 开始获取
    def __get_images(self, word='美女'):
        search = urllib.parse.quote(word)
        while 1:
            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' + search + '&cg=girl' + '&rn=60&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'
            try:
                time.sleep(self.time_sleep)
                req = urllib.request.Request(url=url, headers=self.headers)
                page = urllib.request.urlopen(req)
                rsp = page.read().decode('unicode_escape')
            except UnicodeDecodeError as e:
                pass
                # print(e)
                # print('-----UnicodeDecodeErrorurl:', url)
            except urllib.error.URLError as e:
                pass
                # print(e)
                # print("-----urlErrorurl:", url)
            except socket.timeout as e:
                pass
                # print(e)
                # print("-----socket timout:", url)
            else:
                # 解析json
                rsp_data = json.loads(rsp)
                self.__save_image(rsp_data, word)
            finally:
                page.close()
                break
        return

    def start(self, word):
        self.__get_images(word)

def pic_crawler(keyword=''):
    if keyword == '':
        return -1
    crawler = Crawler(0.05)
    crawler.start(keyword)

if __name__ == '__main__':
    pic_crawler('刘德华')
