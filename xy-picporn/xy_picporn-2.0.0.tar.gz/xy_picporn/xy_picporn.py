import requests
import json
import base64
import os
import math

'''图片标签'''
def pic_porn(filename=''):
    if not filename:
        return -1

    url = 'https://www.phpfamily.org/picPorn.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()

    # print(res['data']['tag_list'][9])
    if res['ret'] == 0 and res['data']:
        resInfo = res['data']['tag_list']
        if resInfo[1]['tag_confidence'] > 50 or resInfo[9]['tag_confidence'] > 30:
            return True
        else:
            return False
    else:
        return -1

def main():
    res = pic_porn('z1.jpg')
    print(res)
if __name__ == '__main__':
    main()
