import requests
import json
import base64
import os
import math

'''美食图片检测'''
def img_food(filename=''):
    if not filename:
        return -1

    url = 'https://www.phpfamily.org/imgFood.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data'] :
        res['data']['confidence'] = str(math.ceil(res['data']['confidence']*100)) + '%'
        return res['data']
    else:
        return -1
def main():
    res = img_food('2.jpg')
    print(res)
if __name__ == '__main__':
    main()
