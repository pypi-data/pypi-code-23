import urllib
import json
import requests

baseUrlCMS = 'https://cms.vip.stratus.ebay.com'
urlCMSQ = '/cms/repositories/cmsdb/branches/main/query/'
value = 'application/json'
headers = {"Content-type": value, "Accept": value}

baseUrlPET = 'https://cms.vip.stratus.ebay.com'

def getCMSToken(CorpPassWord):
    uri = '/cms/validate/user/danyachen'
    headers = {"X-Password": CorpPassWord}
    r = requests.get(baseUrlCMS + uri, params=None, headers=headers)
    if r.status_code == 200:
        token = json.loads(r.text)['token']
        return token
    else:
        raise


# query CMS
def queryCMS(q,CorpPassWord):
    params = urllib.urlencode({'query': q})
    newParams = params[6:len(params)]
    urlParams = urlCMSQ + newParams
    headers = {"Content-type": value, "Accept": value,
               "Authorization": getCMSToken(CorpPassWord)}

    r = requests.get(baseUrlCMS+urlParams, params=None, headers=headers)
    if r.status_code == 200:
        json_result = json.loads(r.text)['result']
        print r.text
        return json_result


if __name__ == "__main__":
    print getCMSToken()