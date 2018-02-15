#coding:utf-8
import ConfigParser
import os
import time
def updateSelf(config,configPath):
    try:
        config.write(open(configPath,'w'))
    except:
        print '目录%s下的配置文件更新失败！！！'%(configPath)
class config():
    exist=False
    def __init__(self):
        self.config=ConfigParser.ConfigParser()
        s='' #s是配置文件初始化所在路径，和configPath是一样的
        for item in self.configPath.split('/'):
            s=s+item+'/'
            if not os.path.exists(s):
                os.mkdir(s)
        if( not os.path.exists(s+'/'+self.configName) )or (len(open(s+'/'+self.configName).read())==0):
            print 'building a new config file ...'
            with open (s+'/'+self.configName,'w') as fp:
                fp.write(self.content)
                print 'building is finished'
                print 'the config file %s is in %s'%(self.configName,s)
        self.config.read(s+'/'+self.configName)
    def getConfig(self,section,key):
        return self.config.get(section,key)
    def setConfig(self,section,key,value):
        self.config.set(section,key,value)
        updateSelf(self.config,self.configPath+'/'+self.configName)
    def addSection(self,section):
        self.config.add_section(section)
        updateSelf(self.config,self.configPath+'/'+self.configName)
    def items(self,section):
        return self.config.items(section)
    def deleteSection(self,section):
        self.config.remove_section(section)
        updateSelf(self.config,self.configPath+'/'+self.configName)
    def deleteOption(self,section,key):
        self.config.remove_option(section,key)
        updateSelf(self.config,self.configPath+'/'+self.configName)
    def isExistOption(self,section,key):
        return self.config.has_option(section,key)

class systemConfig(config):
    path=os.path.split(os.path.abspath(__file__))[0]
    configPath=os.path.split(os.path.split(path)[0])[0]
    configName='system'+'.conf'
    content='''
[check]
[system]
daynum=%s
%s=%s
series=%s
headScript = <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML'></script>
[optional]
series=daily
theme=m1
indexTheme=index1
[theme]
'''%(time.strftime('%d'),
        time.strftime('%d'),
        os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0]+'/bin'+'/md'+'/'+time.strftime('%Y')+'/'+time.strftime('%m')+'/'+time.strftime('%d'),
        os.path.split(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])[0]+'/bin'+'/series')





class userConfig(config):
    path=os.path.split(os.path.abspath(__file__))[0]
    configPath=os.path.split(os.path.split(path)[0])[0]
    configName='user'+'.conf'
    content='''
[user]
userName=Unknown
siteName=Unknown


'''
class pageConfig(config):
    _dayNum=systemConfig().getConfig('system','daynum')
    configPath=systemConfig().getConfig('system',_dayNum)
    configName='page'+'.conf'
    content='''
[page]

'''
class seriesConfig(config):
    configPath=systemConfig().getConfig('system','series')
    print configPath
    configName='series'+'.conf'
    content='''
[series]

'''

if __name__=='__main__':
    systemConfig().setConfig('system','fuckyout','tom')
