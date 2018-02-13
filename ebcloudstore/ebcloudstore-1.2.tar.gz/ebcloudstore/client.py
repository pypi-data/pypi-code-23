# -*- coding: utf-8 -*-
import json
import os
import platform
from io import BufferedReader
from urllib.request import quote

import requests

from ebcloudstore.util import get_file_type_by_ext, IMG_EXTENSION_LIST


class EbStoreAuthException(Exception):
    pass


class EbStoreUploadException(Exception):
    pass


class EbStore(object):
    def __init__(self, token, action="response", callback_url=None, referer=None):
        """
        init the EbStore
        :param token:
        :param action: response|callback|redirect
        :param callback_url:when the action is callback,this params is must
        :param referer:
        :return:
        """
        self.token = token
        self.code = None
        self.file_type = None
        self.ip_list = None
        self.disk = None
        self.action = action
        self.callback_url = callback_url
        self.referer = referer
        self.get_code()

    def get_code(self):
        url = "http://cloud.53iq.com/api/auth"
        r = requests.get(url=url, params={"token": self.token}, timeout=5)
        ret = r.json()
        if ret["code"] == 0:
            self.code = ret["data"]["code"]
            self.file_type = ret["data"]["file_type"]
            self.ip_list = ret["data"]["ip_list"]
            self.disk = int(ret["data"]["disk"])
        else:
            raise EbStoreAuthException(ret["msg"])

    def check_ext(self, file_ext):
        ext_arr = json.loads(self.file_type.replace("'", '"'))
        if "*" in ext_arr:
            return True
        for i in ext_arr:
            if i.lower() == file_ext.lower():
                return True
        return False

    def check_size(self, file_size):
        size = self.disk * 1024
        if size > file_size:
            return True
        else:
            return False

    def check_ip(self, ip):
        ip_arr = json.loads(self.ip_list.replace("'", '"'))
        if "*" in ip_arr:
            return True
        for i in ip_arr:
            if i.lower() == ip.lower():
                return True
        return False

    def upload(self, args, filename=None, file_type=None):
        """
        upload file
        todo:check size
        todo:check ip
        :param args: a full file path or file bytes
        :param filename:
        :param file_type:
        :return:
        """
        if isinstance(args, str):
            if os.path.isfile(args):
                ext_split = os.path.splitext(args)
                filename_prefix, file_extension = ext_split[0], ext_split[1][1:]
                if filename is None:
                    sys_str = platform.system().lower()
                    if sys_str == "windows":
                        filename_prefix = filename_prefix.split("\\")[-1]
                    else:
                        filename_prefix = filename_prefix.split("/")[-1]
                    filename = "%s.%s" % (filename_prefix, file_extension)
                if len(ext_split) >= 2 and self.check_ext(file_extension):
                    filename = quote(filename)
                    if file_type is None:
                        file_type = get_file_type_by_ext(file_extension)
                    files = {'file': (filename, open(args, "rb"), file_type)}
                else:
                    raise EbStoreUploadException("file extension not supported(only support:%s)" % self.file_type)
            else:
                raise EbStoreUploadException("args not file path: %s" % args)
        elif isinstance(args, BufferedReader) or isinstance(args, bytes):
            file_extension = ""
            if filename is None:
                filename = "untitled"
            else:
                ext_split = os.path.splitext(filename)
                if not (len(ext_split) >= 2 and self.check_ext(ext_split[1][1:])):
                    raise EbStoreUploadException("file extension not supported(only support:%s)" % self.file_type)
                file_extension = ext_split[1][1:]

            if file_type is None:
                file_type = get_file_type_by_ext(file_extension)
            filename = quote(filename)

            files = {'file': (filename, args, file_type)}
        else:
            raise EbStoreUploadException("args must be string or BufferedReader or bytes! can't be %s" % (type(args)))

        data = {"code": self.code}
        headers = None
        if self.action == "callback" and self.callback_url is not None:
            data["action"] = self.action
            data["callback_url"] = self.callback_url
        elif self.action == "redirect" and self.referer is not None:
            headers["Referer"] = self.referer
        if headers:
            r = requests.post(url="http://cloud.53iq.com/api/file", files=files, data=data, headers=headers)
        else:
            r = requests.post(url="http://cloud.53iq.com/api/file", files=files, data=data)
        return r.text

    def upload_img(self, file_path, filename=None, file_type=None):
        """
        upload img file
        :param file_path: eg: /your/file/path/hello.jpg
        :param filename: eg:hello.jpg
        :param file_type: eg:image/jpeg
        :return:
        """
        ext_split = os.path.splitext(filename)
        if not (len(ext_split) >= 2 and self.check_ext(ext_split[1][1:])):
            raise EbStoreUploadException("file extension not supported(only support:%s)" % self.file_type)
        file_extension = ext_split[1][1:]
        if file_extension not in IMG_EXTENSION_LIST.keys():
            raise EbStoreUploadException("not image file (only support:%s)" % IMG_EXTENSION_LIST.keys())
        self.upload(file_path, filename, file_type)
