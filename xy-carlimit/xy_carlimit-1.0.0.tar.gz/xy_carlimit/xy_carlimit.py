import urllib.request
import urllib.parse
import json
import os


APPKEY='631c5a5b9992bd74'
APPSECRET='eS0iNTaMdI5mgRew8JkrVqUB7mG1MytS'
API_URL='http://api.jisuapi.com/vehiclelimit/query'

'''汽车限号查询'''
def limit_number(cityname='',datestr=''):
    if not cityname:
        return -1
    data = {}
    data['appkey'] = APPKEY
    data['city'] = cityname
    data['date'] = datestr
    url_values = urllib.parse.urlencode(data)
    url = API_URL + '?' + url_values
    result = urllib.request.urlopen(url)
    jsonarr = json.loads(result.read())
    res = jsonarr['result']
    if res:
        res_str = res['date']+' '+res['week']+os.linesep
        res_str = '限行尾号为：'+res['number']+','+res['numberrule']+os.linesep
        res_str+= '限行区域为：'+res['cityname']+','+res['area']+','+res['summary']+os.linesep
        return res_str
    else:
        return -1


def main():
    print(limit_number('北京'))

if __name__ == '__main__':
    main()
