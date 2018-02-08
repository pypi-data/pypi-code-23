import sys
import json
import base64
import requests
import webbrowser
import wave, pyaudio
import os


def voice2text(filename='', rate=16000,format_type=2):
    '''语音转文字'''
    if not filename:
        return -1
    url = 'https://www.phpfamily.org/speech.php'
    filepath = os.path.abspath(filename)
    b64_data= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['data'] = b64_data
    data['format'] = format_type
    data['rate'] = rate
    r = requests.post(url, data=data)
    res = r.json()
    if res['ret'] == 0 and res['data'] :
        return res['data']['text']
    else:
        return -1

def text2voice(text, filename,model_type=2,speed=0):
    '''文字转语音'''
    if not filename or not text:
        return -1
    if model_type not in (1,2) :
        model_type = 2
    url = 'https://www.phpfamily.org/text2voice.php'
    data = {}
    data['text'] = text
    data['model_type'] = model_type
    data['speed'] = speed
    r = requests.post(url, data=data)
    # print(r.text)
    res = r.json()
    # print(res)
    if res['ret'] == 0 and res['data'] :
        b64_data = base64.b64decode(res['data']['voice'])
        with open(filename,'wb') as f:
            f.write(b64_data)
    return filename

def record(filename, seconds=5, to_dir=None, rate=16000, channels=1, chunk=1024):
    '''录制音频采样率16000'''
    if not filename:
        return -1

    if to_dir is None:
        to_dir = "./"

    pa = pyaudio.PyAudio()
    stream = pa.open(format = pyaudio.paInt16,
                     channels = channels,
                     rate = rate,
                     input = True,
                     frames_per_buffer = chunk)

    print("* 开始录制")

    save_buffer = []
    for i in range(0, int(rate / chunk * seconds)):
        audio_data = stream.read(chunk)
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
    wf.setnchannels(channels)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16,))
    wf.setframerate(rate)
    # join 前的类型
    wf.writeframes(b''.join(save_buffer))
    wf.close()

    return file_path


def main():
    # todo()
    # record1('9.wav')
    # record1('9.mp3')
    # record1('11.wav')
    # print(v2t('11.wav'))
    # print(v2t('12.mp3'))
    # record('1.mp3')
    # record('1.wav')
    # print(voice2text('1.mp3'))
    # text2voice('大家好，欢迎来到小猿编程','2.mp3')
    # text2voice('大家好，欢迎来到小猿编程','2.wav')
    # res = voice2text1('1.mp3')
    # print(res)
    # res = voice2text1('1.wav')
    # print(res)
    #
    # res = voice2text('2.mp3')
    # print(res)
    # res = voice2text('2.wav')
    # print(res)
    # res = v2t('1.wav',8000)
    # print(res)
    # res = v2t('2.wav',16000)
    # print(res)
    # record('3.wav')
    # record('3.mp3')
    # res = v2t('3.wav',8000)
    # print(res)
    # res = v2t('5.wav')
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','4.wav',0)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','5.wav',1)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','6.wav',2)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','7.wav',3)
    # print(res)
    # res = t2v('大家好，欢迎来到猿辅导','8.wav',4)
    # print(res)
if __name__ == '__main__':
    main()
