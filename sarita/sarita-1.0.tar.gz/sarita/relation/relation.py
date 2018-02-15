#coding:utf-8
import sys
import os
import re
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from config import config
import shutil
def changeMdtoHtml(pageConfigPath):
    pageHtmlPath=pageConfigPath[::-1]
    pageHtmlPath=pageHtmlPath.replace('dm','lmth',1)
    pageHtmlPath=pageHtmlPath[::-1]
    return pageHtmlPath
def replace(change,content):
    for pattern,subs in change:
        content=re.sub(pattern,subs,content)
    return content
def makeDayRelation(pageConfig,mds):
    m=0
    for item in mds:
        if item==mds[0]:
            pass
        if item==mds[-1]:
            try:
                if len(mds)<1:
                    with open(pageConfig.getConfig(str(mds[m]),'htmllink'),'r')as f:
                        content=f.read()
                    articlelink=pageConfig.getConfig(str(mds[m]),'articlelink')
                    change=(('href=.*<!---next--->.*<!---next--->',"href=\""+articlelink+"#<!---next---><!---next--->"),
                            ('src=.*<!---next--->.*<!---next--->',"src=\""+articlelink+"#<!---next---><!---next--->"))
                    content=replace(change,content)
                else:
                    with open(pageConfig.getConfig(str(mds[m]),'htmllink'),'r')as f:
                        content=f.read()
                    articlelink=pageConfig.getConfig(str(mds[m]),'articlelink')
                    preArticleLink=pageConfig.getConfig(str(mds[m-1]),'articlelink')
                    print preArticleLink
                    change=(('href=.*<!---next--->.*<!---next--->',"href=\""+articlelink+"#<!---next---><!---next--->"),
                            ('src=.*<!---next--->.*<!---next--->',"src=\""+articlelink+"#<!---next---><!---next--->"),
                            ('href=.*<!---previous--->.*<!---previous--->',"href=\""+preArticleLink+"#<!---previous---><!---previous--->"))
                    content=replace(change,content)
                    
                    with open(pageConfig.getConfig(str(mds[m-1]),'htmllink'),'r')as f:
                        pContent=f.read()
                    change=(('href=.*<!---next--->.*<!---next--->',"href=\""+articlelink+"#<!---next---><!---next--->"),
                            ('src=.*<!---next--->.*<!---next--->',"src=\""+articlelink+"#<!---next---><!---next--->"))
                    pContent=replace(change,pcontent)
                    with open(pageConfig.getConfig(str(mds[m-1]),'htmllink'),'w') as f:
                        f.write(pContent)

                

            except:
                pass
        else:
            try:
                with open(pageConfig.getConfig(str(mds[m]),'htmllink'),'r')as f:
                    content=f.read()
                
                change=(('href=.*<!---previous--->.*<!---previous--->', "href=\""+ pageConfig.getConfig(str(mds[m-1]),'articlelink') +'#<!---previous---><!---previous--->' ),
                        ('href=.*<!---next--->.*<!---next--->', "href=\""+pageConfig.getConfig(str(mds[m+1]),'articlelink')+'#<!---next---><!---next--->')
                        )
                content=replace(change,content)
                
               
            except:
                pass
        try:
            with open(pageConfig.getConfig(str(mds[m]),'htmllink'),'w')as fp:
                    fp.write(content)
        except:
            pass
                
        m=m+1
def noName(path):
    path=path.split('/')
    path.reverse()
    path=path[0:5]
    path.reverse()
    path='./../../../../'+('/').join(path)
    return path



def makeDayDayRelation(pageConfig,systemConfig):
    monNum=systemConfig.getConfig('system','monnum')
    path=systemConfig.getConfig('system',monNum)
    path=changeMdtoHtml(path)
    dates=os.listdir(path)
    intDate=[]
    for item in dates:
        intDate.append(int(item))
    intDate.sort()
    if len(dates)<=0:
        pass
    else:
        m=0
        for item in  intDate:
            if item==intDate[0]:
                pass
            else:
                #找到今天的第一片
                #找到前一天的最后一片
                #前一天的最后一片，改变它的next
                #今天的第一篇，改变它的previous
                #日期加一
                todayPath=path+'/'+str(intDate[m])
                n=[]
                for item in os.listdir(todayPath):
                    n.append(int(item.split('.')[0]))
                n.sort()
                firstInToday=todayPath+'/'+str(n[0])+'.html'
                FarticlePath=noName(firstInToday)




                yestodayPath=path+'/'+str(intDate[m-1])
                n=[]
                for item in os.listdir(yestodayPath):
                    n.append(int(item.split('.')[0]))
                n.sort()
                lastInYestoday=yestodayPath+'/'+str(n[-1])+'.html'
                LarticlePath=noName(lastInYestoday)
                with open(lastInYestoday,'r') as f:
                    lastContent=f.read()
                change=(('href=.*<!---next--->.*<!---next--->',"href=\""+FarticlePath+'#<!---next---><!---next--->'),
                        ('href=.*<!---next--->.*<!---next--->',"href=\""+FarticlePath+'#<!---next---><!---next--->')
                        )
                lastContent=replace(change,lastContent)
                with open(lastInYestoday,'w')as f:
                    f.write(lastContent)

                with open(firstInToday,'r')as f:
                    firstContent=f.read()
                change=(('href=.*<!---previous--->.*<!---previous--->',"href=\""+LarticlePath+'#<!---previous---><!---previous--->'),
                        ('href=.*<!---previous--->.*<!---previous--->',"href=\""+LarticlePath+'#<!---previous---><!---previous--->')
                        )
                firstContent=replace(change,firstContent)
                with open(firstInToday,'w')as f:
                    f.write(firstContent)



            m=m+1


            




def makeMonthRelation(systemConfig,mds):
    yearNum=systemConfig.getConfig('system','yearnum')
    yearPath=systemConfig.getConfig('system',yearNum)
    yearPath=noName(yearPath)
    months=os.listdir(yearPath)
    intMonths=[]
    for item in months:
        intMonths.append(int(item))
    intMonths.sort()
    #未完待续





class relation():
    def __init__(self):
        systemConfig=config.systemConfig()
        pageConfig=config.pageConfig()
        pageConfigPath=pageConfig.configPath
        pageHtmlPath=changeMdtoHtml(pageConfigPath)
        if len(os.listdir(pageConfigPath))<=1:
            shutil.rmtree(pageConfigPath)
            shutil.rmtree(pageHtmlPath)
            sys.exit()
        mds=[]
        for item in os.listdir(pageConfigPath):
            try:
                mds.append(int(item.split('.')[0]))
            except:
                pass
        mds.sort()
        makeDayRelation(pageConfig,mds)
        makeDayDayRelation(pageConfig,systemConfig)
        makeMonthRelation(systemConfig,mds)






        
