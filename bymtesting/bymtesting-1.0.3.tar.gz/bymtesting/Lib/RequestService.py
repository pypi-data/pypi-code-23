import requests
from requests import Response
import sys
import re
import os


class RequestToken:
    headerJson = {'Accept': 'application/json'}

    @staticmethod
    def setToken(token):
        RequestToken.headerJson = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token
        }

    @staticmethod
    def getToken(token):
        return RequestToken.headerJson

    @staticmethod
    def removeToken():
        RequestToken.headerJson = {'Accept': 'application/json'}


class RequestService:
    def get(self, url):
        output = "GET " + url
        result = requests.get(url, headers=RequestToken.headerJson)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += 'Text: {}'.format(result.text)
        print(output)
        return result

    def GetFileFullPath(self, filename):
        currentDir = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(currentDir, filename)
        return fullpath

    def downloadFile(self, url):
        output = "GET " + url
        result = requests.get(
            url, headers=RequestToken.headerJson, stream=True)
        if result.status_code is not 200:
            output += '{} {}'.format(result.status_code, result.reason)
            print(output)
        else:
            filename = result.headers['Content-Disposition']
            filename = re.findall("filename=(.+);", filename)
            filename = filename[0]
            file = self.GetFileFullPath(filename)
            with open(file, 'wb') as f:
                for chunk in result.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
        return result

    # payload must be a dict like so => {'mmm': 'kay'}
    def post(self, url, payload):
        output = "POST " + url
        result = requests.post(
            url, headers=RequestToken.headerJson, json=payload)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += u'{}'.format(sys.stdout.encoding)
            errorText = u'Text: {}'.format(result.text)
            print(errorText.encode(sys.stdout.encoding, errors='replace'))
        print(output)
        return result

    def put(self, url, payload):
        output = "PUT " + url
        result = requests.put(
            url, headers=RequestToken.headerJson, json=payload)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += 'Text: {}'.format(result.text)
        print(output)
        return result

    def generic(self, url, verb):
        if (verb == 'get'):
            result = requests.get(url, headers=RequestToken.headerJson)
        elif (verb == 'post'):
            result = requests.post(url, headers=RequestToken.headerJson)
        elif (verb == 'put'):
            result = requests.put(url, headers=RequestToken.headerJson)
        elif (verb == 'delete'):
            result = requests.delete(url, headers=RequestToken.headerJson)

        if (result.ok == False):
            print('{} {}'.format(result.status_code, result.reason))
            print('Text: {}'.format(result.text))
        return result

    def delete(self, url):
        output = "DELETE " + url
        result = requests.delete(url, headers=RequestToken.headerJson)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += 'Text: {}'.format(result.text)
        print(output)
        return result

    def post_with_files(self, url, payload, files):
        output = "POST " + url
        result = requests.post(
            url, files=files, data=payload, headers=RequestToken.headerJson)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += 'Text: {}'.format(result.text)
        print(output)
        return result

    def put_with_files(self, url, payload, files):
        output = "PUT " + url
        result = requests.put(
            url, files=files, data=payload, headers=RequestToken.headerJson)
        if (result.ok == False):
            output += '{} {}'.format(result.status_code, result.reason)
            output += 'Text: {}'.format(result.text)
        print(output)
        return result
