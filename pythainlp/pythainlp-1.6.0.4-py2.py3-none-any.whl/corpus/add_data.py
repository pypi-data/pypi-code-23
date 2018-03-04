# -*- coding: utf-8 -*-
import re
import codecs
# โปรแกรมเปรียบเทียบข้อมูลคำใน 2 ไฟล์
def get_data(file):
	with codecs.open(file, 'r',encoding='utf8') as f:
		lines = f.read()
	f.close
	return re.split("\n",lines)
file1=list(set(get_data("thaiword.txt")))
file2=list(set(get_data("tnc201705.txt"))) # ไฟล์ที่ต้องการเทียบ
i=0
x=0
word=[]
while i<len(file1):
	if file1[i] in file2:
		x+=1
		word.append(file1[i])
	else:
		word.append(file1[i])
	i+=1
i=0
while i<len(file2):
	if ((file2[i] in file1)==False):
		word.append(file2[i])
	i+=1
a = codecs.open('newdict.txt', 'w',encoding='utf8')
a.write("\n".join(word))
a.close
print("OK")