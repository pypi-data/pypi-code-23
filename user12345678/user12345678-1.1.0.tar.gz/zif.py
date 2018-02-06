import zipfile
# #压缩
# file=zipfile.ZipFile('text.zip','w')#text.zip创建压缩包文件名 w读
# file.write("class.py")#压缩的文件名
# file.close()

#解压缩
# file=zipfile.ZipFile('text.zip','r')#写
# file.extractall(path="../")#写到哪个路径下  创建到卓面 默认是在跟慕入下面

#暴力破解加密的压缩包
fileobj=open("pwd.txt","r")#新建一个txt文件
for item in fileobj.readlines():
    print(item.strip())#strip()去空格
    newpwd=item.strip()
    try:
        file=zipfile.ZipFile("class2.zip","r")#解压缩包
        file.extractall(pwd=newpwd.encode("utf-8"))
    except:
        print("errot")
