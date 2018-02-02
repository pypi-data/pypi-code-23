import re


class 提出通用音標:

    @classmethod
    def 揣音標(cls, trs聽拍):
        trs聽拍 = trs聽拍.strip()
        trs聽拍 = re.sub(r'\[//\]', '-X-', trs聽拍)
        trs聽拍 = re.sub(
            r'([a-z]+\d)\[([a-z]+\d)\]', lambda x: x.group(2), trs聽拍
        )  # 原本的修正lexicon
        trs聽拍 = re.sub(
            r'([a-z]+\d)\+ \[([a-z]+\d)\] ', lambda x: x.group(2), trs聽拍
        )  # 轉textgrid的修正lexicon

        class 外語詞紀錄:
            def __init__(self):
                self._紀錄 = set()

            def 轉外詞詞(self, x):
                self._紀錄 |= set(x.group(1))
                return x.group(1)

            def 提紀錄(self):
                return ''.join(self._紀錄 - {'+', '-', '[', ']'})
        紀錄 = 外語詞紀錄()
        trs聽拍 = re.sub(
            r'\[\w*-\]([^\]]+)\[-\w*\]', 紀錄.轉外詞詞, trs聽拍
        )
        trs聽拍 = re.sub(r'\[[^\]]*\]', ' ', trs聽拍)
        trs聽拍 = re.sub(r'\([^\)]*\)', '', trs聽拍)
        if trs聽拍.endswith('//'):
            答案 = re.sub(r'[^a-z0-9/]*//', ' ', trs聽拍).strip()
        elif '/' in trs聽拍:
            答案 = re.sub(r'.*/', '', trs聽拍)
        else:
            答案 = re.sub(
                r'.*[^a-zA-Z0-9\- _,+{}]'.format(紀錄.提紀錄()), '', trs聽拍)
        return 答案.strip()
