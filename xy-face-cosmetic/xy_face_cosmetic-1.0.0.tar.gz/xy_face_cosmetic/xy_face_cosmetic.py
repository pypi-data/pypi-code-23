import requests
import json
import base64
import os
import math

'''人脸美妆'''
def face_cosmetic(filename='', cosmetic=1):
    if not filename:
        return -1
    if cosmetic < 1:
        cosmetic = 1
    if cosmetic > 23:
        cosmetic = 23
    url = 'https://www.phpfamily.org/faceCosmetic.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['cosmetic'] = cosmetic
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'meiyan_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1

'''获取美妆类型'''
def cosmetic_type():
    COSMETIC_TYPE = {
    1:'日系妆-芭比粉',
    13:'韩妆-玫瑰',
    2:'日系妆-清透',
    14:'裸妆-自然',
    3:'日系妆-烟灰',
    15:'裸妆-清透',
    4:'日系妆-自然',
    16:'裸妆-桃粉',
    5:'日系妆-樱花粉',
    17:'裸妆-橘粉',
    6:'日系妆-原宿红',
    18:'裸妆-春夏',
    7:'韩妆-闪亮',
    19:'裸妆-秋冬',
    8:'韩妆-粉紫',
    20:'主题妆-经典复古',
    9:'韩妆-粉嫩',
    21:'主题妆-性感混血',
    10:'韩妆-自然',
    22:'主题妆-炫彩明眸',
    11:'韩妆-清透',
    23:'主题妆-紫色魅惑',
    12:'韩妆-大地色'
    }
    return COSMETIC_TYPE

def main():
    res = face_cosmetic('1.jpg',23)
    print(res)
    res = cosmetic_type()
    print(res)
if __name__ == '__main__':
    main()
