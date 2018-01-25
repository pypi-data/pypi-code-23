import requests
import json
import base64
import os
import math

'''制作大头贴'''
def face_sticker(filename='', sticker=2):
    if not filename:
        return -1
    if sticker < 1:
        sticker = 1
    if sticker > 31:
        sticker = 31
    url = 'https://www.phpfamily.org/faceSticker.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['sticker'] = sticker
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'facesticker_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1

'''返回大头贴背景类型'''
def sticker_type():
    STICKER_TYPE = {
    1:	'NewDay',
    2:	'欢乐球吃球1:',
    3:	'Bonvoyage',
    4:	'Enjoy',
    5:	'ChickenSpring',
    6:	'ChristmasShow',
    7:	'ChristmasSnow',
    8:	'CircleCat',
    9:	'CircleMouse',
    10:	'CirclePig',
    11:	'Comicmn',
    12:	'CuteBaby',
    13:	'Envolope',
    14:	'Fairytale',
    15:	'GoodNight',
    16:	'HalloweenNight',
    17:	'LovelyDay',
    18:	'Newyear2017',
    19:	'PinkSunny',
    20:	'KIRAKIRA',
    21:	'欢乐球吃球2:',
    22:	'SnowWhite',
    23:	'SuperStar',
    24:	'WonderfulWork',
    25:	'Cold',
    26:	'狼人杀守卫',
    27:	'狼人杀猎人',
    28:	'狼人杀预言家',
    29:	'狼人杀村民',
    30:	'狼人杀女巫',
    31:	'狼人杀狼人'
    }
    return STICKER_TYPE


def main():
    res = face_sticker('1.jpg')
    print(res)
    res = sticker_type()
    print(res)

if __name__ == '__main__':
    main()
