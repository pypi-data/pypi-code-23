#!/usr/bin/python3

"""
@author: 张伟
@time: 2018/3/7 9:28
"""
import os


class Mate(object):
    data = list()
    text = str()

    def __init__(self, thesaurus_path=os.getcwd(), filename='words', field=4):
        """
        初始化
        :param thesaurus_path  词库文件父目录。默认是项目下
        :param filename: 词库文件名字，文件应放在本项目根目录下
        :param field:  最大粒度
        """
        self.thesaurus_path = thesaurus_path
        self.field = field
        self.filename = filename
        self.p = os.path.altsep
        self.load()

    def load(self):
        """
        加载字典，默认初始化自动加载
        :return: None
        """
        with open(os.path.join(self.thesaurus_path, self.filename), encoding='utf-8-sig') as f:
            self.data = [f[:-1] for f in f.readlines()]

    def mate(self, input_txt, output_txt, encode='utf-8-sig'):
        """
        分词文本
        :param input_txt:  输入文本
        :param output_txt: 输出文本
        :param encode: 编码，默认是UTF-8模式
        :return: None
        """
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
