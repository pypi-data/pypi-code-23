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
    data['token'] = _get_access_token()
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
def what(filename=''):
    '''返回动物的种类，例如猫、犬、虎、羊'''
    if not filename:
        return -1
    res = _info(filename)
    if res and res != '非动物':
        res = res.replace('犬','狗')
        res = res.replace('梗','狗')
        res = res.replace('多','狗')
        res = res.replace('基','狗')
        res = res.replace('奇','狗')
        res = res.replace('加','狗')
        res = res.replace('巴','狗')
        res = res.replace('八','狗')
        res = res.replace('美','狗')
        res = res.replace('迪','狗')
        return res[-1:]
    else:
        return '这不是一个动物哟~'

def breed(filename=''):
    '''返回动物的名称，例如金毛犬'''
    if not filename:
        return -1
    res = _info(filename)
    if res and res != '非动物':
        res = res.replace('犬','狗')
        return res
    else:
        return '这不是一个动物哟~'

def sound(text=''):
    '''播放动物的叫声'''
    dir_res = os.path.abspath(__file__)
    dir_res = os.path.dirname(dir_res)
    if text not in ('猫','犬','虎','鸟','狗','羊'):
        os.system(dir_res+'/data/error.mp3')
    else:
        sound_dict = {
            '猫':'cat.mp3',
            '犬':'dog.mp3',
            '狗':'dog.mp3',
            '鸟':'bird.mp3',
            '羊':'sheep.mp3',
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
    data['token'] = _get_access_token()
    data['topNum'] = topNum
    r = requests.post(url, data=data)
    res = r.json()
    if res['result'] :
        if topNum == 1:
            return res['result'][0]['name']
        else:
            return res['result']

def main():
    # print(type(_get_access_token()))
    # print(_get_access_token())
    # res = animal('1.jpg')
    # print(res)


if __name__ == '__main__':
    main()
