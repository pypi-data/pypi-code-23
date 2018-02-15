#coding:utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('../')
from relation import relation
from config import config
import markdown
import re
from theme import theme
def cutContent(opcontent,number):
    content=opcontent
    content.reverse()
    warn='Conversion Failed:\nYou may have DESTORYED the config words when you editing!!!\nYou may edit your article bellow the config words\n'
    try:
        a=content.index('notes:\n')
        b=content.index('compose on the top of these words plz\n')
        c=content.index('please write title on the first line\n')
        d=content.index('you can change the choices but do not destroy these words!!!\n')
        if d==(c-1):
            if c==(b-1):
                if b==(a-1):
                    pass
                else:
                    raise UserWarning(warn)
            else:
                raise UserWarning(warn)
        else:
            raise UserWarning(warn)
    except ValueError:
        print warn
        sys.exit()
    except UserWarning:
        print warn
        sys.exit()
    configContent=content[0:a+1]
    configContent.reverse()
    articleContent=content[a+1::]
    isEmpty=True
    for item in articleContent:
        item=item.strip()
        if item =='':
            pass
        elif item=='\n':
            pass
        else:
            isEmpty=False
    if isEmpty:
        print '未编辑，已退出'
        if os.path.exists(config.pageConfig().getConfig(number,'path')):
            os.remove(config.pageConfig().getConfig(number,'path'))
            config.pageConfig().deleteSection(number)
        relation()
        sys.exit()


    articleContent.reverse()
    title=articleContent[0]
    del articleContent[0]
    return title,articleContent,configContent

def readConfigContent(content,title,number):
    pageConfig=config.pageConfig()
    pageConfig.setConfig(number,'title',title)
    for item in content:
        if item.find('=')>=0:
            key=item.split('=')[0]
            value=item.split('=')[1]
            pageConfig.setConfig(number,key,value)
        else:
            pass
def initHtml(html,themeName):
    themePath=config.systemConfig().getConfig('system','sources')+'/'+themeName+'/'
    for item in os.listdir(themePath):
        sourcesPattern="href\={1}\".*"+item+"\""
        html=re.sub(sourcesPattern,"href=\"./../../../../sources/"+themeName+'/'+item+"\"",html)
    for item in os.listdir(themePath):
        sourcesPattern="src\={1}\".*"+item+"\""
        html=re.sub(sourcesPattern,"src=\"./../../../../sources/"+themeName+'/'+item+"\"",html)
    return html
def replace(articleHtml,number):
    pageConfig=config.pageConfig()
    systemConfig=config.systemConfig()
    userConfig=config.userConfig()
    theme1=pageConfig.getConfig(number,'theme')
    m=systemConfig.getConfig('theme','m').split(' ')
    if not theme1 in m:
        print 'No theme %s'%(theme1)
        print 'Please Check'
        sys.exit()
    html=theme().useTheme(theme1)
    html=initHtml(html,theme1)
    if html=='':
        print "Didn't find the theme" 
        sys.exit()
    htmlPath=systemConfig.getConfig('system',systemConfig.getConfig('system','dayNum'))
    htmlPath=htmlPath[::-1]
    htmlPath=htmlPath.replace('dm','lmth',1)
    htmlPath=htmlPath[::-1]+'/'+number+'.html'
    a=htmlPath
    htmlPath=htmlPath[htmlPath.index('html')::]
    htmlPath='./../../../../'+htmlPath
    pageConfig.setConfig(number,'htmlLink',a)
    pageConfig.setConfig(number,'articleLink',htmlPath)
    avatar=userConfig.getConfig('user','avatar')
    if userConfig.getConfig('user','avatar').find('http://')<0:
        if userConfig.getConfig('user','avatar').find('https://')<0:
            avatar='./../../../../'+userConfig.getConfig('user','avatar')
    navigation=''
    try:
        for item,navLinks in systemConfig.items('navigation'):
            navigation=navigation+'<a href="%s">%s</a>'%(navLinks,item)
    except: 
        pass
    change=(('<!---article---><!---article--->',articleHtml),
            ('<!---articletitle---><!---articletitle--->',pageConfig.getConfig(number,'title')),
            ('<!---username---><!---username--->',userConfig.getConfig('user','userName')),
            ('<!---sitename---><!---sitename--->',userConfig.getConfig('user','userName')),
            ('<!---articledate---><!---articledate--->',systemConfig.getConfig('system','time')),
            ('<!---userquote---><!---userquote--->',userConfig.getConfig('user','quote')),
            ('<!---copyright---><!---copyright--->',userConfig.getConfig('user','copyright')),
            ('<!---useravatar---><!---useravatar--->',avatar),
            ('<!---ariclelink---><!---ariclelink--->',pageConfig.getConfig(number,'articleLink')),
            ('<!---email---><!---email--->','mailto:'+userConfig.getConfig('user','email')),
            ('<!---github---><!---github--->',userConfig.getConfig('user','github')),
            ('<!---sitelink---><!---sitelink--->','./'),
            ('</head>',systemConfig.getConfig('system','headScript')+'</head>'),
            ('<!---nav---><!---nav--->',navigation),
    )
    
    for pattern,subs in change:
        html=re.sub(pattern,subs,html)

    return html,a

def writeIn(html,path):
    with open(path,'w')as f:
        f.write(html)




def m2h(content):
    exts=['markdown.extensions.extra','markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    articleHtml=markdown.markdown(content,extensions=exts)
    return articleHtml
def handleArticleContent(content,number):
    content=''.join(content)#把ｌｉｓｔ变为ｓｔｒ
    articleHtml=m2h(content)
    html,htmlPath=replace(articleHtml,number)
    writeIn(html,htmlPath)
    
    



class md2html():
    def __init__(self,mdPath):
        number=os.path.split(mdPath)[1].split('.')[0]
        with open(mdPath,'r')as f:
            self.content=f.readlines()
        title,articleContent,configContent=cutContent(self.content,number)
        readConfigContent(configContent,title,number)
        handleArticleContent(articleContent,number)

