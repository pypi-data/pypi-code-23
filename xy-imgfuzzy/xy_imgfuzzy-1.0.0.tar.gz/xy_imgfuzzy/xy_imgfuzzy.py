import requests
import json
import base64
import os
import math

'''图片模糊度查询'''
def img_fuzzy(filename=''):
    if not filename:
        return -1

    url = 'https://www.phpfamily.org/imgFuzzy.php'
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
    # # res = img_fuzzy('1.jpeg')
    # # print(res)
    res = img_fuzzy('2.jpg')
    print(res)
if __name__ == '__main__':
    main()
