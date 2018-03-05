import urllib.request
import urllib.parse
import json
import os


def jizhuanwan(keyword=''):
    '''脑筋急转弯'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/jzw/search'
    data = {}
    data['appkey'] = APPKEY
    data['pagesize'] = 1
    data['pagenum'] = 1
    data['keyword'] = keyword
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_dict = {}
        res_dict['answer']=res['list'][0]['answer']
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['content'] + os.linesep + '答案：' + res_dict['answer']
        return res_str
    else:
        return -1




def raokouling(keyword=''):
    '''绕口令'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/rkl/search'
    data = {}
    data['appkey'] = APPKEY
    data['pagesize'] = 1
    data['pagenum'] = 1
    data['keyword'] = keyword
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_dict = {}
        res_dict['title']=res['list'][0]['title']
        # res_dict['content']=res['list'][0]['content'].replace('<br />',os.linesep)
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['title'] + os.linesep + '答案：' + res_dict['content']
        return res_str
    else:
        return -1



def xiehouyu(keyword=''):
    '''歇后语'''
    APPKEY='631c5a5b9992bd74'
    APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
    API_URL='http://api.jisuapi.com/xhy/search'
    data = {}
    data['appkey'] = APPKEY
    data['pagesize'] = 1
    data['pagenum'] = 1
    data['keyword'] = keyword
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_dict = {}
        res_dict['answer']=res['list'][0]['answer']
        res_dict['content']=res['list'][0]['content'].replace('<br />','')
        res_str = '问题：' + res_dict['content'] + os.linesep + '答案：' + res_dict['answer']
        return res_str
    else:
        return -1


def main():
    print(jizhuanwan())
    print(raokouling())
    print(xiehouyu())

if __name__ == '__main__':
    main()
