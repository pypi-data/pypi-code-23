import requests
import json
import base64
import os
import math

'''人脸美妆'''
def face_decoration(filename='', decoration=1):
    if not filename:
        return -1
    if decoration < 1:
        decoration = 1
    if decoration > 22:
        decoration = 22
    url = 'https://www.phpfamily.org/faceDecoration.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['decoration'] = decoration
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'bianzhuang_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1

'''获取美妆类型'''
def decoration_type():
    DECORATION_TYPE = {
    1:'埃及妆',
    2:'巴西土著妆',
    3:'灰姑娘妆',
    4:'恶魔妆',
    5:'武媚娘妆',
    6:'星光薰衣草',
    7:'花千骨',
    8:'僵尸妆',
    9:'爱国妆',
    10:'小胡子妆',
    11:'美羊羊妆',
    12:'火影鸣人妆',
    13:'刀马旦妆',
    14:'泡泡妆',
    15:'桃花妆',
    16:'女皇妆',
    17:'权志龙',
    18:'撩妹妆',
    19:'印第安妆',
    20:'印度妆',
    21:'萌兔妆',
    22:'大圣妆'
    }
    return DECORATION_TYPE

def main():
    res = face_decoration('1.jpg')
    print(res)
    res = decoration_type()
    print(res)
if __name__ == '__main__':
    main()
