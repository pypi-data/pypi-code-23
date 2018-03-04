# -*- coding: utf-8 -*-
import time
start_time = time.time()
from pythainlp.tokenize import word_tokenize
print("PyThaiNLP newmm")
print(word_tokenize("จุ๋มเป็นอย่างไรบ้าง"))
print(word_tokenize("จุ๋มเป็นอย่างไรบ้างkkuน่ารักมาก"))
print(word_tokenize("นัน ผมหลงรักคุณมาsvdsxรนนืแล้วนันปลุกไฟภาษาไทย20หน่วยกิตมหาวิทยาลัยขอนแก่นวิทยาเขตหนองคายkkunkc"))
print(word_tokenize("""นัน ผมหลงรักคุณมาsvdsxรนนืแล้วนันปลุกไฟภาษาไทย20หน่วยกิตมหาวิทยาลัยขอนแก่นวิทยาเขตหนองคาย
kkunkc	ok"""))
print("--- %s seconds ---" % (time.time() - start_time))