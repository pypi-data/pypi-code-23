import requests
import json
import base64
import os
import math

'''人物图片添加滤镜'''
def person_filter(filename='', filter_type=1):
    if not filename:
        return -1
    if filter_type < 1:
        filter_type = 1
    if filter_type > 22:
        filter_type = 22
    url = 'https://www.phpfamily.org/personFilter.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['filter'] = filter_type
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'personfilter_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1

'''获取人物滤镜类型'''
def person_filter_type():
    PERSON_FILTER_TYPE = {1:'黛紫',2:'岩井',3:'粉嫩',4:'错觉',5:'暖阳',6:'浪漫',7:'蔷薇',
    8:'睡莲',9:'糖果玫瑰',10:'新叶',11:'尤加利',12:'墨',13:'玫瑰初雪',14:'樱桃布丁',15:'白茶',
    16:'甜薄荷',17:'樱红',18:'圣代',19:'莫斯科',20:'冲绳',21:'粉碧',22:'地中海',23:'首尔',
    24:'佛罗伦萨',25:'札幌',26:'栀子',27:'东京',28:'昭和',29:'自然',30:'清逸',31:'染',32:'甜美'}
    return PERSON_FILTER_TYPE


'''风景图片添加滤镜'''
def scenery_filter(filename='', filter_type=1):
    if not filename:
        return -1
    if filter_type < 1:
        filter_type = 1
    if filter_type > 22:
        filter_type = 22
    url = 'https://www.phpfamily.org/sceneryFilter.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['filter'] = filter_type
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'sceneryfilter_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1

'''风景图片滤镜类型'''
def scenery_filter_type():
    SCENERY_FILTER_TYPE = {}
    return SCENERY_FILTER_TYPE


def main():
    res = scenery_filter('1.jpg',22)
    print(res)
    res = person_filter_type()
    print(res)

if __name__ == '__main__':
    main()
