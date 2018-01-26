#!/usr/bin/env python
# -*- coding: utf-8 -*-


class AutoPackConfig(object):
    """docstring for AutoPackConfig"""

    def __init__(self, flavors):
        super(AutoPackConfig, self).__init__()
        self.flavors = flavors
        self.dirName = 'default'
        self.suffix = ''
        self.prefix = ''
        self.useVersionSuffix = False

    # 渠道包生成后输出的目录
    def setDestDirName(self, dirName):
        self.dirName = dirName

    # 使用固定的后缀
    def useSpecificSuffix(self, suffix):
        self.suffix = suffix
        self.useVersionSuffix = False

    # 使用版本号后缀
    def enableVersionSuffix(self):
        self.useVersionSuffix = True

    # 设置前缀
    def setPrefix(self, prefix):
        self.prefix = prefix

    # 渠道包生成后存为的文件名
    def getSaveAsFileName(self, flavor, apkInfo):
        destFileName = flavor
        if self.prefix and len(self.prefix) > 0:
            destFileName = self.prefix + '_' + destFileName
        if self.suffix and len(self.suffix) > 0:
            destFileName += ('_' + self.suffix)
        else:
            if self.useVersionSuffix:
                destFileName += ('_' + apkInfo.versionName)
        return destFileName+".apk"