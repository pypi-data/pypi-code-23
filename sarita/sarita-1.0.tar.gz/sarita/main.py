#coding:utf-8

#                       .::::.
#                     .::::::::.
#                    :::::::::::
#                 ..:::::::::::'
#              '::::::::::::'
#                .::::::::::
#           '::::::::::::::..
#                ..::::::::::::.
#              ``::::::::::::::::
#               ::::``:::::::::'        .:::.
#              ::::'   ':::::'       .::::::::.
#            .::::'      ::::     .:::::::'::::.
#           .:::'       :::::  .:::::::::' ':::::.
#          .::'        :::::.:::::::::'      ':::::.
#         .::'         ::::::::::::::'         ``::::.
#     ...:::           ::::::::::::'              ``::.
#    ```` ':.          ':::::::::'                  ::::..
#                       '.:::::'                    ':'````..
#               Godness,plz give me a girl


from check import check
from inputPara import inputPara
from edit import edit
from md2html import md2html
from relation import relation
import os
import sys



def main():
    check()
    command=inputPara().whatCommand()
    if 'new' in command:
        content=edit(1)
        mdPath=content.mdPath
    else:
        content=edit()
        mdPath=content.mdPath
    md2html(mdPath)
    relation()
    

    



if __name__=='__main__':
    main()
