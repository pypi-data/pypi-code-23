import requests
import json
import base64
import os
# import cv2
import time
from PIL import Image

# def camera():
#     cap = cv2.VideoCapture(0)
#     while(1):
#         ret, frame = cap.read()
#         cv2.imshow("capture", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             now = time.localtime()
#             filename = str(now.tm_year) + str(now.tm_mon) + str(now.tm_mday) + str(now.tm_hour) + str(now.tm_min) + str(now.tm_sec) + '.jpg'
#             cv2.imwrite(filename, frame)
#             break
#     cap.release()
#     cv2.destroyAllWindows()
#     return filename

def _resize_img(filepath,max_size=512000):
    # MAX_FILE_SIZE = max_size
    filesize = os.path.getsize(filepath)
    # if filesize > MAX_FILE_SIZE :
    im = Image.open(filepath)
    src_w = im.size[0]
    src_h = im.size[1]
    dst_w = 460
    dst_h = (src_h/src_w) * 460
    dst_size = dst_w , dst_h
    im.thumbnail(dst_size)
    im.save(filepath)
    return filepath

def _getInfo(filename='', mode=0):
    url = 'https://www.phpfamily.org/faceInfo.php'
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)
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
        return res_dict
    else:
        return -1

def gender1(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return res['gender']

def gender(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return '男' if res['gender']>90 else '女'

def age(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return res['age']

def glass1(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return bool(res['glass'])

def glass(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return res['glass']

def beauty(filename=''):
    if not filename:
        return -1
    res = _getInfo(filename)
    return res['beauty']

'''识别图片中一张人脸信息'''
def info(filename='', mode=0):
    if not filename:
        return -1
    filepath = os.path.abspath(filename)
    filepath = _resize_img(filepath)

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
        res_str = '{gender}，{age}岁左右，{glass}眼镜，颜值打分：{beauty}分'.format(gender=gender,age=res_dict['age'],glass=glass,beauty=res_dict['beauty'])
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
            res_str += '第{i}个人脸信息：{gender}，{age}岁左右，{glass}眼镜，颜值打分：{beauty}分'.format(gender=gender,age=val['age'],glass=glass,beauty=val['beauty'],i=i)
            res_str += os.linesep
            i += 1
        return res_str
    else:
        return '图片中找不到人哦~'



def main():
    # pass
    print(info('1.jpg'))
    # filename = camera()
    # res = age(filename)
    # print(res)
    # res = gender(filename)
    # print(res)
    # res = glass(filename)
    # print(res)
    # res = beauty(filename)
    # print(res)
    # res = info('2.jpg')
    # print(res)
    # res = info_all('3.jpg')
    # print(res)
    # res = age('5.jpg')
    # print(res)
    # res = gender('5.jpg')
    # print(res)
    # res = glass('5.jpg')
    # print(res)
    # res = beauty('5.jpg')
    # print(res)


if __name__ == '__main__':
    main()
