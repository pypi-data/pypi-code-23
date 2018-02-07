import requests
import json
import base64
import os

# def _check_imgsize(filepath,max_size=512000):
#     MAX_FILE_SIZE = max_size
#     filesize = os.path.getsize(filepath)
#     if filesize > MAX_FILE_SIZE :
#         dir_res = os.path.abspath(__file__)
#         dir_res = os.path.dirname(dir_res)
#         shutil.copy(dir_res+'/data/error.png',os.path.dirname(filepath)+'/error.png')
#         print('error.png')
#         return False
#     return True

'''识别图片中一张人脸信息'''
def info(filename='', mode=0):
    if not filename:
        return -1
    # filepath = os.path.abspath(filename)
    # if not _check_imgsize(filepath,1048576):
    #     return -1
    url = 'https://www.phpfamily.org/faceInfo.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['mode'] = mode
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['face_list'][0]
        res_dict = {
        'age':res['age'],
        'gender':res['gender'],
        'beauty':res['beauty'],
        'glass':res['glass']
        }
        gender =  '男性' if res_dict['gender'] >= 50 else '女性'
        glass = '戴' if res_dict['glass'] else '不戴'
        res_str = '{gender},{age}岁左右,{glass}眼镜,颜值打分:{beauty}分'.format(gender=gender,age=res_dict['age'],glass=glass,beauty=res_dict['beauty'])
        return res_str
    else:
        return '图片中找不到人哦~'

'''返回图片中所有人脸信息'''
def info_all(filename='', mode=0):
    if not filename:
        return -1
    # filepath = os.path.abspath(filename)
    # if not _check_imgsize(filepath,1048576):
    #     return -1
    url = 'https://www.phpfamily.org/faceInfo.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['mode'] = mode
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data']:
        res = res['data']['face_list']
        res_str = '图片中总共发现{face_len}张人脸：'.format(face_len=len(res))+os.linesep
        i = 1
        for val in res :
            gender =  '男性' if val['gender'] >= 50 else '女性'
            glass = '戴' if val['glass'] else '不戴'
            res_str += '第{i}个人脸信息：{gender},{age}岁左右,{glass}眼镜,颜值打分:{beauty}分'.format(gender=gender,age=val['age'],glass=glass,beauty=val['beauty'],i=i)
            res_str += os.linesep
            i += 1
        return res_str
    else:
        return '图片中找不到人哦~'



def main():
    res = info('2.jpg')
    print(res)
    res = info_all('3.jpg')
    print(res)


if __name__ == '__main__':
    main()
