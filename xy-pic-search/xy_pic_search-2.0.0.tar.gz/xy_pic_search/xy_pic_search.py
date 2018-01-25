import re
import os.path
import time
from random import randint
import requests


def pic_search(keyword='', total=10):
    '''简单的根据搜索内容进行批量图片下载'''
    if keyword == '':
        return -1
    url = 'http://image.baidu.com/search/index?tn=baiduimage&ie=utf-8&word='+keyword
    result = requests.get(url).text
    pic_url = re.findall('"objURL":"(.*?)",',result,re.S)
    url_count = len(pic_url)
    if url_count < 1 :
        return -1
    if total >= url_count:
        total = url_count
    i = 0
    print( '找到关键词:'+keyword+'的图片，现在开始下载图片...')
    for each in pic_url:
        if i == total:
            break
        print( '正在下载第'+str(i+1)+'张图片，图片地址:'+str(each))
        try:
            pic= requests.get(each, timeout=10)
        except requests.exceptions.ConnectionError:
            print( '【错误】当前图片无法下载')
            continue
        dir_path = keyword
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        hms=time.strftime('%H%M%S',time.localtime(time.time()))+'.'+str(randint(1000,9999))
        string = dir_path + '/' + keyword + '_'+str(i) + '_' + hms + '.jpg'
        fp = open(string,'wb')
        fp.write(pic.content)
        fp.close()
        i += 1

def main():
    pic_search('彭于晏')

if __name__ == '__main__':
    main()
