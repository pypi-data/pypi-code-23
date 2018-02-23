import requests
import json
import base64
import os
import math

def check(filename=''):
    '''美食图片检测'''
    if not filename:
        return False

    url = 'https://www.phpfamily.org/imgFoodCheck.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data'] :
        res['data']['confidence'] = str(math.ceil(res['data']['confidence']*100)) + '%'
        return res['data']['food']
    else:
        return False
def main():
    res = food_check('2.jpg')
    print(res)
if __name__ == '__main__':
    main()
