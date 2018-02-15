#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from config import config
class theme():
    def __init__(self):
        systemConfig=config.systemConfig()
        themePath=systemConfig.getConfig('system','theme')
        allTheme= os.listdir(themePath)
        m=''
        index=''
        other=''
        for item in allTheme:
            if os.path.isfile(themePath+'/'+item):
                if item.find('.')>=0:
                    name=item.split('.')[0]
                    if name[0]=="m":
                        m=m+' '+name
                    elif name[0]=="i":
                        index=index+' '+name
                    else:
                        other=other+' '+name+' '

        systemConfig.setConfig('theme','m',m)
        systemConfig.setConfig('theme','index',index)
        systemConfig.setConfig('theme','other',other)
    def useTheme(self,name):
        systemConfig=config.systemConfig()
        themePath=systemConfig.getConfig('system','theme')
        try:
            with open(themePath+'/'+name+'.html','r')as f:
                content=f.read()
        except IOError:
            print 'no %s'%(name)
            return ''
        return content



                

                



