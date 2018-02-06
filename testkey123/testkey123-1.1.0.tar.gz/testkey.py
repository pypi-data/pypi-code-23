from urllib import request
def testkey():
    response = request.urlopen("http://www.baidu.com/")
    print(response.read())
