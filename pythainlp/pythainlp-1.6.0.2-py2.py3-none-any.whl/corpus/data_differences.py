# -*- coding: utf-8 -*-
import re
import codecs
# โปรแกรมเปรียบเทียบข้อมูลคำใน 2 ไฟล์
def get_data(file):
	with codecs.open(file, 'r',encoding='utf8') as f:
		lines = f.read()
	return re.split("\n",lines)
file1=list(set(get_data("thaiword.txt")))
file2=list(set(get_data("tnc201705.txt"))) # ไฟล์ที่ต้องการเทียบ
i=0
x=0
while i<len(file1):
	if file1[i] in file2:
		x+=1
	i+=1
print("มีข้อมูลไฟล์ 1 ใน 2 คิดเป็น "+str((x/len(file1))*100)+" % จากข้อมูลทั้งหมดใน file1")
print("ข้อมูลไฟล์ 2 มีจำนวน " + str(len(file2))+" คำ")