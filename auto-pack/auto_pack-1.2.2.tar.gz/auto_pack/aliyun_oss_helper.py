# -*- coding: utf-8 -*-

import os
import sys
import shutil
import oss2
import progressbar
import getopt

from progressbar import ProgressBar, Percentage, Bar

access_key_id = os.getenv('OSS_QUFENQI_ACCESS_KEY_ID', None)
access_key_secret = os.getenv('OSS_QUFENQI_ACCESS_KEY_SECRET', None)
bucket_name = os.getenv('OSS_BUCKET_QUFENQI_MOBILE_ANDROID', None)
endpoint = os.getenv('OSS_QUFENQI_ENDPOINT', None)
pbar = progressbar.ProgressBar(widgets=[Percentage(), Bar()], maxval=100)
for param in (access_key_id, access_key_secret, bucket_name, endpoint):
    assert '<' not in param, '请设置参数：' + param
bucket = oss2.Bucket(
    oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
fileName = ''


def percentage(consumed_bytes, total_bytes):
    """进度条回调函数，计算当前完成的百分比

    :param consumed_bytes: 已经上传/下载的数据量
    :param total_bytes: 总数据量
    """
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        pbar.update(rate)

    if consumed_bytes >= total_bytes:
        pbar.finish()


def uploadDir(dirPath):
    files = os.listdir(dirPath)
    description = '将上传以下文件:\n'

    validFiles = []
    for i in range(0, len(files)):
        file_path = os.path.join(dirPath, files[i])
        if os.path.isfile(file_path):
            validFiles.append(file_path)
            description += ("%1d:%2s\n" % (len(validFiles), file_path))

    if len(validFiles) == 0:
        print("目录不能为空")
        return
    result = query_yes_no("%1s确认?" % description)
    if result:
        for i in range(0, len(validFiles)):
            uploadFile(validFiles[i])
    else:
        print("已取消上传")


def uploadFile(filePath):
    print('\n创建上传任务:')
    print('待传文件:%1s' % filePath)
    global fileName
    fileName = os.path.basename(filePath)
    pbar.start()
    bucket.put_object_from_file(
        fileName, filePath, progress_callback=percentage)
    print("上传结果:成功")
    print("下载地址:https://static001.qufenqi.com/mobile/android/%1s\n" % fileName)


def query_yes_no(question, default="yes"):

    print("--------------------------------------")

    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def uploadToAliyun(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "i:", ["ifile="])
    except getopt.GetoptError:
        print('请输入的文件路径')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg

    if len(inputfile) > 0:
        if os.path.isfile(inputfile):
            result = query_yes_no("将上传以下文件:\n%1s\n确认?" % inputfile)
            if result:
                uploadFile(inputfile)
            else:
                print("已取消上传")
        elif os.path.isdir(inputfile):
            uploadDir(inputfile)
        else:
            print('找不到文件')
    else:
        print('请输入的文件路径')
