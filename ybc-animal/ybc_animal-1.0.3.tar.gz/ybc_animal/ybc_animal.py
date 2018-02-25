import requests
import json
import base64
import os
import sys
import os.path


def _get_access_token():
    url = 'https://www.phpfamily.org/aniToken.php'
    r = requests.post(url)
    res = r.json()
    return res['access_token']

def _info(filename='',topNum=1):
    url = 'https://www.phpfamily.org/imgAni.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['access_token'] = _get_access_token()
    data['topNum'] = topNum
    r = requests.post(url, data=data)
    res = r.json()
    if res['result'] :
        if topNum == 1:
            return res['result'][0]['name']
        else:
            return res['result']
    else:
        return False
def check(filename=''):
    '''返回动物的种类，例如猫、犬、虎、鸟'''
    if not filename:
        return -1
    res = _info(filename)
    if(res):
        return res[-1:]
    else:
        return False

def animal(filename=''):
    '''返回动物的名称，例如金毛犬'''
    if not filename:
        return -1
    res = _info(filename)
    return res

def sound(text=''):
    '''播放动物的叫声'''
    dir_res = os.path.abspath(__file__)
    dir_res = os.path.dirname(dir_res)
    if text not in ('猫','犬','虎','鸟','狗'):
        os.system(dir_res+'/data/error.mp3')
    else:
        sound_dict = {
            '猫':'cat.mp3',
            '犬':'dog.mp3',
            '狗':'dog.mp3',
            '鸟':'bird.mp3',
            '虎':'tiger.mp3'
        }
        filepath = dir_res+'/data/'+sound_dict[text]
        os.system(filepath)


'''动物识别'''
def animal1(filename='', topNum=1):
    if not filename:
        return -1
    url = 'https://www.phpfamily.org/imgAni.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['access_token'] = _get_access_token()
    data['topNum'] = topNum
    r = requests.post(url, data=data)
    res = r.json()
    if res['result'] :
        if topNum == 1:
            return res['result'][0]['name']
        else:
            return res['result']

def main():
    res = animal('1.jpg')
    print(res)


if __name__ == '__main__':
    main()
