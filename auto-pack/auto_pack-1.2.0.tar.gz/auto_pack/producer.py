#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import zipfile
import os
import sys
import re
import android_utils
import shutil
from pack_config import AutoPackConfig
from pkg_resources import resource_string
FILE_APK_BACK = '_back.apk'
APK_SUFFIX = '.apk'
EMPTY_FILE = 'empty_file'

originApkFileName = None
apkInfo = None
baseDir = None


class FlavorApkProducer(object):
    """docstring for FlavorApkProducer"""

    def __init__(self):
        super(FlavorApkProducer, self).__init__()
        self.prepare()

    def fromFile(self, filePath):
        flavors = []
        file = open(filePath)
        for line in file:
            line = line.strip()
            flavors.append(line)
        self.autoPackConfig = AutoPackConfig(flavors)
        return self

    def enableVersionSuffix(self):
        self.autoPackConfig.enableVersionSuffix()
        return self

    def withPrefix(self, prefix):
        self.autoPackConfig.setPrefix(prefix)
        return self

    def useSpecificSuffix(self, prefix):
        self.autoPackConfig.useSpecificSuffix(prefix)
        return self

    def getAllDestFileNames(self):
        destFileNames = []
        for i in range(len(self.autoPackConfig.flavors)):
            flavor = self.autoPackConfig.flavors[i]
            destFileNames.append(
                self.autoPackConfig.getSaveAsFileName(flavor, self.apkInfo))
        return destFileNames

    def intoDir(self, dirName):
        self.autoPackConfig.setDestDirName(dirName)
        self.produceApks(self.autoPackConfig)
        self.finish()

    def prepare(self):
        if(os.path.exists(FILE_APK_BACK)):
            os.remove(FILE_APK_BACK)
        if not os.path.exists(EMPTY_FILE):
            emptyFile = open(EMPTY_FILE, "wb")
            emptyFile.close()
        self.originApkFileName = self.findOriginalApk()
        if not self.originApkFileName:
            print("找不到母包")
            exit()
        self.apkInfo = android_utils.getApkInfo(self.originApkFileName)
        self.baseDir = 'exportApk/' + self.apkInfo.packageName.replace(".", "_") + "/" + \
            self.apkInfo.versionCode

    def finish(self):
        if(os.path.exists(EMPTY_FILE)):
            os.remove(EMPTY_FILE)
        if(os.path.exists(FILE_APK_BACK)):
            os.remove(FILE_APK_BACK)

    def produceApks(self, autoPackConfig):
        if autoPackConfig:
            if not autoPackConfig.dirName:
                print("需要设置输出目录")
                return
            destDir = self.baseDir + "/" + autoPackConfig.dirName
            if(os.path.exists(destDir)):
                shutil.rmtree(destDir)
            for flavorIndex in range(len(autoPackConfig.flavors)):
                flavor = autoPackConfig.flavors[flavorIndex]
                shutil.copyfile(self.originApkFileName, FILE_APK_BACK)
                zipped = zipfile.ZipFile(
                    FILE_APK_BACK, 'a', zipfile.ZIP_DEFLATED)
                empty_channel_file = "META-INF/topitchannel_{channel}".format(
                    channel=flavor)
                zipped.write(EMPTY_FILE, empty_channel_file)
                zipped.close()
                if not os.path.exists(destDir):
                    os.makedirs(destDir)
                destFileName = autoPackConfig.getSaveAsFileName(
                    flavor, self.apkInfo)
                shutil.move(FILE_APK_BACK, destDir + '/' + destFileName)

    def findOriginalApk(self):
        files = os.listdir('.')
        for i in files:
            i = i.strip()
            if i.endswith(".apk"):
                return i
