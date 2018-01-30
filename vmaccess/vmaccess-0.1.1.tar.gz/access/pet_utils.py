import urllib
import json
import requests

baseUrlDev = 'http://petpoc-2011349.phx02.dev.ebayc3.com:8080'
baseUrlProd = 'https://pet.vip.ebay.com'

value = 'application/json'
headers = {"Content-type": 'application/x-www-form-urlencoded', "Accept": value}

def getPetToken():
    uri = '/ups/api/obtain-auth-token/'
    data = {'username':'danyachen','password':'petdevpassword'}
    r = requests.post(baseUrlDev + uri, data=data)
    print r.text
    if r.status_code == 200:
        token = json.loads(r.text)['token']
        return 'Token ' + token
    else:
        raise

def is_user_in_group(user,group):
    uri = '/ups/api/qa/ldap/user-netgroup/' + group
    r = requests.get(baseUrlDev + uri, headers={'Authorization':getPetToken()})

    if r.status_code == 200:
        userArray =json.loads(r.text)['users']
        print userArray
        if user in userArray:
            return True
        else:
            return False
    else:
        print '-------------------Can not find gourp ---------------------:' + group
        return False

def request_join_group(user, group):
    uri = '/ups/api/qa/ldap/user-netgroup/'+group+'/account/'+user+'/'
    r = requests.put(baseUrlDev+uri, headers={'Authorization':getPetToken()})
    print r.text
    pass

if __name__ == "__main__":
    pass
