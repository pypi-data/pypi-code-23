import urllib.request
import urllib.parse
import json
import re

APPKEY='631c5a5b9992bd74'
API_URL='http://api.jisuapi.com/translate/translate'

def en2zh(text=''):
    '''英译汉'''
    if text == '':
        return -1
    data = {}
    data["appkey"] = APPKEY
    data["type"] = "baidu"
    data["from"] = "en"
    data["to"] = "zh-cn"
    data["text"] = text

    url_values = urllib.parse.urlencode(data)
    url = API_URL + "?" + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res['result']:
        res['result'] = res['result'].replace('<br />','')
        dr = re.compile('<[^>]+>',re.S)
        res_str = dr.sub('',res['result']).strip()
        return res_str
    else:
        return -1

def zh2en(text=''):
    '''汉译英'''
    if text == '':
        return -1
    data = {}
    data["appkey"] = APPKEY
    data["type"] = "baidu"
    data["from"] = "zh-cn"
    data["to"] = "en"
    data["text"] = text

    url_values = urllib.parse.urlencode(data)
    url = API_URL + "?" + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res['result']:
        res['result'] = res['result'].replace('<br />','')
        dr = re.compile('<[^>]+>',re.S)
        res_str = dr.sub('',res['result']).strip()
        return res_str
    else:
        return -1

def main():
    print(zh2en('苹果'))

if __name__ == '__main__':
    main()
