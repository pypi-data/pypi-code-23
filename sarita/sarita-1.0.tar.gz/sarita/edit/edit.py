#coding:utf-8

#调用这个类，得到内容属性
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from config import config
from theme import theme
def vim(path):
    try:
        os.system('vim '+path)
    except:
        print "Error: Didn't find editor Vim on your computer\nYou maight haven't install it or set right system path\nIn this program, Vim is the default Editor, if you don't like it, you can change the sourde code in %s and I like to help"%(os.path.abspath(__file__))
        sys.exit()


def preContent(number):
    systemConfig=config.systemConfig()
    try:
        systemConfig.addSection('optional')
    except:
        pass
    contents=('series','theme','m','indexTheme','index')
    instead=[]
    for item in contents:
        if item in ('m','index'):
            instead.append(systemConfig.getConfig('theme',item))
        else:
            instead.append(systemConfig.getConfig('optional',item))
    instead=tuple(instead)
    content='''












notes:
compose on the top of these words plz
please write title on the first line
you can change the choices but do not destroy these words!!!
series=%s

theme=%s
choices of theme: %s
indexTheme=%s
choices of indexTheme: %s
'''
    content=content%instead

    return content
def creatMd(path,number):
    systemConfig=config.systemConfig()
    pageConfig=config.pageConfig()
    if not os.path.exists(path+'/'+str(number)+'.md'):
        with open(path+'/'+str(number)+'.md','w')as f:
            f.write(preContent(str(number)))
    try:
        pageConfig.addSection(str(number))
    except:
        pass
    pageConfig.setConfig(str(number),'path',path+'/'+str(number)+'.md')
    vim(path+'/'+str(number)+'.md')
    return path+'/'+str(number)+'.md'

class edit():
    def __init__(self,number=0):
        systemConfig=config.systemConfig()
        dayNum=systemConfig.getConfig('system','daynum')
        dayPath=systemConfig.getConfig('system',dayNum)
        if number==1:
            number=systemConfig.getConfig('system','post')
            number=int(number)-1
            if number==-1:
                number=0
            number=str(number)
        self.mdPath=creatMd(dayPath,number)


