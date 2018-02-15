#coding:utf-8
#检查目录的完整性
##获取系统信息，更新系统配置文件
import os
import platform
import sys
import time
import shutil
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from config import config
from theme import theme
def mkdir(tree):
    systemConfig=config.systemConfig()
    systemPath=systemConfig.getConfig('system','systemPath')
    oldFather='systemPath'
    fatherPath=systemPath
    for (father,son) in tree:
        if not oldFather==father:
            oldFather=father
            fatherPath=systemConfig.getConfig('system',father)
        if not os.path.exists(fatherPath+'/'+son):
            os.mkdir(fatherPath+'/'+son)
        systemConfig.setConfig('system',son,fatherPath+'/'+son)
def moveThemeSources():
    systemConfig=config.systemConfig()
    themePath=systemConfig.getConfig('system','theme')
    for item in os.listdir(themePath):
        if not os.path.isfile(themePath+'/'+item):
            if os.path.exists(systemConfig.getConfig('system','sources')+'/'+item):
                shutil.rmtree(systemConfig.getConfig('system','sources')+'/'+item)
                shutil.copytree(themePath+'/'+item,systemConfig.getConfig('system','sources')+'/'+item)
            else:
                shutil.copytree(themePath+'/'+item,systemConfig.getConfig('system','sources')+'/'+item)
def howManyPost():
    systemConfig=config.systemConfig()
    dayNum=systemConfig.getConfig('system','daynum')
    dayPath=systemConfig.getConfig('system',dayNum)
    systemConfig.setConfig('system','post',len(os.listdir(dayPath)))

    

class check():
    path=os.path.split(os.path.abspath(__file__))[0]
    def __init__(self):
        systemConfig=config.systemConfig()
        systemInfo={'systemPath':os.path.split(os.path.split(self.path)[0])[0],
                'os':platform.system(),
                'pythonVersion':platform.python_version(),
                'pythonPath':sys.executable,
                'configPath':systemConfig.configPath,
                'yearNum':time.strftime('%Y'),
                'monNum':time.strftime('%m'),
                'dayNum':time.strftime('%d'),
                'time':time.strftime('%B %d, %Y')

                }
        for item in systemInfo:
            systemConfig.setConfig('system',item,systemInfo[item])
        yearNum=systemConfig.getConfig('system','yearNum')
        monNum=systemConfig.getConfig('system','monNum')
        dayNum=systemConfig.getConfig('system','dayNum')



        #检查并创建目录，复制主题
        tree=(('systemPath','bin'),('systemPath','theme'),
                ('bin','html'),('bin','md'),('bin','series'),('bin','sources'),
                ('html',yearNum),(yearNum,monNum),(monNum,dayNum),
                ('md',yearNum),(yearNum,monNum),(monNum,dayNum)
              ) 
        if systemConfig.isExistOption('system',str(int(yearNum)-1)):
            systemConfig.deleteOption('system',str(int(yearNum)-1))
        mkdir(tree)   
        moveThemeSources()
        config.pageConfig()
        config.userConfig()
        config.seriesConfig()
        theme()
        howManyPost()



if __name__=='__main__':
    check()
