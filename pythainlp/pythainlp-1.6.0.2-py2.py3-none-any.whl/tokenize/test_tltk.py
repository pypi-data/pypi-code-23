# -*- coding: utf-8 -*-
import time
start_time = time.time()
import tltk
print("tltk")
print(tltk.nlp.word_segment("จุ๋มเป็นอย่างไรบ้าง"))
print(tltk.nlp.word_segment("จุ๋มเป็นอย่างไรบ้างkkuน่ารักมาก"))
print(tltk.nlp.word_segment("""นัน ผมหลงรักคุณมาsvdsxรนนืแล้วนันปลุกไฟภาษาไทย20หน่วยกิตมหาวิทยาลัยขอนแก่นวิทยาเขตหนองคาย
kkunkc	ok"""))
print("--- %s seconds ---" % (time.time() - start_time))