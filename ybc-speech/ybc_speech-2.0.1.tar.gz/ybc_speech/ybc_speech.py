import sys
import json
import time
import base64
import urllib.request as req
import urllib.parse as urlp
import requests
import webbrowser
import wave, pyaudio
import xy_pinyin


CU_ID = 'testai'
API_KEY = 'zbZo970ra5cjjP3IMECPW8lZ'
API_SECERT = 'L2BN2GRXWiPDqC5HRL8H9hQI5r4Tz2af'
CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5
URLS = {
    'baidu':'http://www.baidu.com',
    'google':'http://www.google.com',
    'yuanfudao':'http://yuanfudao.com',
    'cat':'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word=%E7%8C%AB',
    'dog':'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1515408520455_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E7%8B%97',
    'xiaoyuan':'http://www.yuanfudao.com/info/emojis'
}

'''
tex	必填	合成的文本，使用UTF-8编码。小于512个中文字或者英文数字。（文本在百度服务器内转换为GBK后，长度必须小于1024字节）
tok	必填	开放平台获取到的开发者access_token（见上面的“鉴权认证机制”段落）
cuid	必填	用户唯一标识，用来区分用户，计算UV值。建议填写能区分用户的机器 MAC 地址或 IMEI 码，长度为60字符以内
ctp	必填	客户端类型选择，web端填写固定值1
lan	必填	固定值zh。语言选择,目前只有中英文混合模式，填写固定值zh
spd	选填	语速，取值0-9，默认为5中语速
pit	选填	音调，取值0-9，默认为5中语调
vol	选填	音量，取值0-15，默认为5中音量
per	选填	发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
'''
getvoice_url = 'http://tsn.baidu.com/text2audio?tex=%s&lan=zh&cuid=%s&ctp=1&tok=%s&spd=5&pit=5&vol=5&per=0'
upvoice_url = 'http://vop.baidu.com/server_api'

'''获取token'''
def get_token(api_key, api_secert):
    token_url = 'http://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'
    token_url = token_url % (api_key, api_secert)
    r_str = req.urlopen(token_url).read()
    token_data = json.loads(r_str)
    token_str = token_data['access_token']
    return token_str

'''语音合成,百度合成语音无法识别，生成的音频无采样位数，所以无法识别，可以使用record方法录制音频，或者识别音频位数为16，采样速率16000的音频来识别'''
def text2voice(text, filename):
    if not text or not filename:
        return -1
    token_str = get_token(API_KEY,API_SECERT)
    get_url = getvoice_url % (urlp.quote(text), CU_ID, token_str)
    voice_data = req.urlopen(get_url).read()
    voice_fp = open(filename,'wb+')
    voice_fp.write(voice_data)
    voice_fp.close()
    return filename

'''语音识别 识别采样速率为16000的，如果音频采样速率为8000，可以使用voice2text1'''
def voice2text(filename):
    if not filename:
        return -1
    token_str = get_token(API_KEY,API_SECERT)
    data = {}
    data['format'] = 'wav'
    data['rate'] = '16000'
    data['channel'] = 1
    data['cuid'] = CU_ID
    data['token'] = token_str

    wav_fp = open(filename,'rb')
    voice_data = wav_fp.read()
    wav_fp.close()
    data['len'] = len(voice_data)
    data['speech'] = base64.b64encode(voice_data).decode('utf-8')
    result = requests.post(upvoice_url, json=data, headers={'Content-Type':'application/json'})
    data_result = result.json()
    if data_result['err_no'] == 0:
        return data_result['result'][0].strip().strip('，')
    else:
        return -1

''' 采样速率8000 '''
def voice2text1(filename):
    if not filename:
        return -1
    token_str = get_token(API_KEY,API_SECERT)
    data = {}
    data['format'] = 'wav'
    data['rate'] = 8000
    data['channel'] = 1
    data['cuid'] = CU_ID
    data['token'] = token_str

    wav_fp = open(filename,'rb')
    voice_data = wav_fp.read()
    wav_fp.close()
    data['len'] = len(voice_data)
    data['speech'] = base64.b64encode(voice_data).decode('utf-8')
    result = requests.post(upvoice_url, json=data, headers={'Content-Type':'application/json'})
    data_result = result.json()
    if data_result['err_no'] == 0:
        return data_result['result'][0].strip().strip('，')
    else:
        return -1

''' 录制音频'''
def record(filename, seconds=RECORD_SECONDS, to_dir=None):

    if not filename:
        return -1

    if to_dir is None:
        to_dir = "./"

    pa = pyaudio.PyAudio()
    stream = pa.open(format = FORMAT,
                     channels = CHANNELS,
                     rate = RATE,
                     input = True,
                     frames_per_buffer = CHUNK)

    print("* 开始录制")

    save_buffer = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        audio_data = stream.read(CHUNK)
        save_buffer.append(audio_data)

    print("* 结束录制")

    # stop
    stream.stop_stream()
    stream.close()
    pa.terminate()

    if to_dir.endswith('/'):
        file_path = to_dir + filename
    else:
        file_path = to_dir + "/" + filename

    # save file
    wf = wave.open(file_path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pa.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    # join 前的类型
    wf.writeframes(b''.join(save_buffer))
    wf.close()

    return file_path

''' 打开指定网址'''
def browser_open_text(text):
    if not text:
        return -1
    res = xy_pinyin.pin1(text)
    res = res.replace('-','')
    if res.startswith("baidu") or res.startswith("bai"):
        url = URLS['baidu']
    elif res.startswith("guge") or res.startswith("google"):
        url = URLS['google']
    elif res.startswith('yuanfudao') or res.startswith('yuan'):
        url = URLS['yuanfudao']
    elif res.startswith('xiaoyuan') or res.startswith('xiao'):
        url = URLS['xiaoyuan']
    elif res.startswith('cat') or res.startswith('mao'):
        url = URLS['cat']
    elif res.startswith('dog') or res.startswith('gou'):
        url = URLS['dog']
    else:
        url = "http://www.baidu.com"

    return webbrowser.open_new_tab(url)


def main():
    # record('1.mp3')
    # record('1.wav')
    # print(voice2text('1.mp3'))
    # text2voice('大家好，欢迎来到小猿编程','2.mp3')
    # text2voice('大家好，欢迎来到小猿编程','2.wav')
    res = voice2text1('1.mp3')
    print(res)
    res = voice2text1('1.wav')
    print(res)

    res = voice2text('2.mp3')
    print(res)
    res = voice2text('2.wav')
    print(res)
if __name__ == '__main__':
    main()
