#!/usr/bin/python3

"""
@author: 张伟
@time: 2018/3/7 9:28
"""
import os


class Mate(object):
    thesaurus_path = os.getcwd()
    data = list()
    text = str()

    def __init__(self, filename='words', field=4):
        self.field = field
        self.filename = filename
        self.p = os.path.altsep
        self.load()

    def load(self):
        with open(os.path.join(self.thesaurus_path, self.filename), encoding='utf-8-sig') as f:
            self.data = [f[:-1] for f in f.readlines()]

    def mate(self, input_txt, output_txt, encode='utf-8-sig'):
        with open(input_txt, 'r+', encoding=encode) as f:
            self.text = f.read()
        w = open(output_txt, 'w+', encoding=encode)
        lens = len(self.text) - self.field + 1
        j = 0
        flag = 0
        while j < lens:
            for k in range(j + 2, j + 1 + self.field):
                word = self.text[j:k]
                deviation = 1
                while word in self.data:
                    word = self.text[j:k + deviation]
                    deviation += 1
                if deviation != 1:
                    if self.text[flag:j] not in '':
                        w.write(self.text[flag:j] + self.p)
                    w.write(word[:-1] + self.p)
                    w.flush()
                    j = k + deviation - 2
                    flag = j
                    j -= 1
                    break
            j += 1
        w.write(self.text[flag:])
        w.flush()
        w.close()
