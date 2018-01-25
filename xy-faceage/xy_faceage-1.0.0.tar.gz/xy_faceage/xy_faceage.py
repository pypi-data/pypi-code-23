import requests
import json
import base64
import os
import math

'''识别照片的颜值和年龄，返回图片'''
def face_age(filename=''):
    if not filename:
        return -1
    url = 'https://www.phpfamily.org/faceAge.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        new_file = 'faceage_'+filename
        with open(new_file,'wb') as f:
            f.write(base64.b64decode(res['data']['image']))
        return new_file
    else:
        return -1





def main():
    res = face_age('1.jpg')
    print(res)


if __name__ == '__main__':
    main()
