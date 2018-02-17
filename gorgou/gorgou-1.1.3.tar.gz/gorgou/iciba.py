#!/usr/bin/env python
# -*- coding: utf8 -*-


import os, requests, json
dire = os.path.dirname(os.path.abspath(__file__))


def get_mp3(db_word, pen_dir=dire):
    purl = 'http://fy.iciba.com/ajax.php?a=fy&w=' + db_word
    ptext = requests.get(purl).text
    obj = json.loads(ptext)
    pstatus = obj['status']
    pcontent = obj['content']
    if pstatus == 0:
        cn_mean = pcontent['word_mean']
        br_vo = pcontent['ph_en']
        am_vo = pcontent['ph_am']
        en_mp3 = pcontent['ph_en_mp3']
        am_mp3 = pcontent['ph_am_mp3']

        pcontent = requests.get(en_mp3).content
        pen_mp3 = os.path.join(pen_dir + '/', db_word + '.mp3')
        with open(pen_mp3, 'wb') as f:
            f.write(pcontent)

        return cn_mean
