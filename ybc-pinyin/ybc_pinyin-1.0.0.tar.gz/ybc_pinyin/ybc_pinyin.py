from pypinyin import pinyin, lazy_pinyin, Style

'''返回带音标的'''
def pin(text=''):
    if text == '':
        return -1
    res = pinyin(text)
    res_list = []
    for s in res:
        res_list.append(s[0])
    return '-'.join(res_list)

'''返回不带音标的'''
def pin1(text=''):
    if text == '':
        return -1
    return '-'.join(lazy_pinyin(text))

'''得到多音字'''
def duoyin(text=''):
    if text == '' or len(text) != 1:
        return -1
    res = pinyin(text,heteronym=True)
    res_list = []
    for s in res[0]:
        res_list.append(s)
    return '-'.join(res_list)
