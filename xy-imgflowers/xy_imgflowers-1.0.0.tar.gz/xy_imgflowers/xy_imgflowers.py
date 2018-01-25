import requests
import json
import base64
import os

'''花草树木识别'''
def flowers_recognition(filename=''):
    if not filename:
        return -1

    url = 'https://www.phpfamily.org/imgFlowers.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    r = requests.post(url, data=data)
    res = r.json()
    print(res)

def main():
    res = flowers_recognition('1.jpg')
    print(res)
if __name__ == '__main__':
    main()
