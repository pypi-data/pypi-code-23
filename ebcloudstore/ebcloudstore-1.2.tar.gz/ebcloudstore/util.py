# -*- coding: utf-8 -*-
EXTENSION_LIST = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "application/x-bmp",

    "mp3": "audio/mp3",

    "mp4": "video/mp4",
    "avi": "video/avi",

    "zip": "application/x-zip-compressed",
    "rar": "application/octet-stream",
    "js": "application/x-javascript",
    "css": "text/css",
    "json": "application/json",
    "apk": "application/vnd.android.package-archive",
    "xls": "application/-excel",
    "doc": "application/msword",
    "exe": "application/x-msdownload",
    "txt": "text/plain",
    "htm": "text/html",
    "html": "text/html",
}

IMG_EXTENSION_LIST = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "bmp": "application/x-bmp",
}


def get_file_type_by_ext(extension):
    """
    :param extension: eg: png
    :return:
    """
    if not extension:
        return "application/octet-stream"
    extension = extension.lower()
    if extension not in EXTENSION_LIST.keys():
        return "application/octet-stream"
    return EXTENSION_LIST[extension]


def is_cn_char(cnt):
    """
    check is contain chinese
    :param cnt:
    :return:
    """
    is_cn = False
    for i in cnt:
        is_cn = 0x4e00 <= ord(i) < 0x9fa6
        if is_cn:
            break
    return is_cn


def cn2char(cnt):
    """
    chinese to char
    :param cnt:
    :return:
    """
    ret = ""
    for i in cnt:
        is_cn = 0x4e00 <= ord(i) < 0x9fa6
        if is_cn:
            ret += hex(ord(i))
        else:
            ret += i
    return ret
