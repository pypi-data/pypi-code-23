import gzip
from os.path import dirname
import pickle
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.音標系統.閩南語.臺灣閩南語羅馬字拼音 import 臺灣閩南語羅馬字拼音
from 臺灣言語工具.基本物件.詞 import 詞
from 臺灣言語工具.語言模型.KenLM語言模型訓練 import KenLM語言模型訓練
from 臺灣言語工具.辭典.型音辭典 import 型音辭典
from 臺灣言語工具.語音合成.閩南語音韻.變調.規則變調 import 規則變調
from 程式.全漢全羅.語料路徑 import 語料路徑

漢字本調分開符號 = '|'


def 檔案加入辭典(檔案, 辭典):
    全部詞 = set()
    for line in 檔案:
        句物件 = 拆文分析器.分詞句物件(line.strip())
        for 詞物件 in 句物件.網出詞物件():
            全部詞.add(詞物件)
    for 第幾詞, 詞物件 in enumerate(全部詞):
        辭典看資料(辭典, 詞物件)
        for 字物件 in 詞物件.內底字:
            辭典看資料(辭典, 字物件)
        第幾詞 += 1
        if 第幾詞 % 100 == 0:
            print('匯入第 {} 詞'.format(第幾詞))


def 變調(音, 海口腔):
    拼音 = 臺灣閩南語羅馬字拼音(音)
    if 拼音.調 == '6':
        拼音.調 = '7'
    if 拼音.音標 is not None:
        拼音.聲, 拼音.韻, 拼音.調 = 規則變調.變調((拼音.聲, 拼音.韻, 拼音.調))
        if 海口腔:
            拼音.調 = '3'
        拼音.做音標()
        return 拼音.音標
    return 音


def 辭典看資料(辭典, 物件):
    for 詞物件 in 可能的變調(物件):
        辭典.加詞(詞物件)


def 可能的變調(物件):
    yield from _一个腔口的變調(物件, False)
    yield from _一个腔口的變調(物件, True)


def _一个腔口的變調(物件, 海口腔):
    尾字無變調詞物件 = 詞(物件.篩出字物件())
    字陣列 = 尾字無變調詞物件.內底字
    for 字物件 in 字陣列:
        字物件.型 = 字物件.型 + 漢字本調分開符號 + 字物件.音
    for 所在 in range(len(字陣列) - 1):
        字陣列[所在].音 = 變調(字陣列[所在].音, 海口腔)
    yield 尾字無變調詞物件

    尾字有變調詞物件 = 詞(字陣列)
    尾字有變調詞物件.內底字[-1].音 = 變調(尾字有變調詞物件.內底字[-1].音, 海口腔)
    yield 尾字有變調詞物件

    尾字無變h8詞物件 = 詞(物件.篩出字物件())
    for 字物件 in 尾字無變h8詞物件.內底字:
        字物件.型 = 字物件.型 + 漢字本調分開符號 + 字物件.音
    for 所在 in range(len(字陣列) - 1):
        字物件 = 尾字無變h8詞物件.內底字[所在]
        if 字物件.音.endswith('h4'):
            字物件.音 = 字物件.音.replace('h4', 'h8')
        elif 字物件.音.endswith('h8'):
            字物件.音 = 字物件.音.replace('h8', 'h10')
        else:
            字物件.音 = 變調(字物件.音, 海口腔)
    yield 尾字無變h8詞物件

    尾字有變調h8詞物件 = 詞(尾字無變h8詞物件.內底字)
    字物件 = 尾字有變調h8詞物件.內底字[-1]
    if 字物件.音.endswith('h4'):
        字物件.音 = 字物件.音.replace('h4', 'h8')
    elif 字物件.音.endswith('h8'):
        字物件.音 = 字物件.音.replace('h8', 'h10')
    else:
        字物件.音 = 變調(字物件.音, 海口腔)
    yield 尾字有變調h8詞物件


def 做():
    KenLM語言模型訓練().訓練([語料路徑.原始一對一語料()], dirname(語料路徑.斷詞語言模型()))
    辭典 = 型音辭典(4)
#     辭典 = 現掀辭典(4)
    with gzip.open(語料路徑.原始一對一語料(), 'rt') as f:
        檔案加入辭典(f, 辭典)
    with gzip.open(語料路徑.斷詞典(), 'wb') as f:
        pickle.dump(辭典, f, protocol=pickle.HIGHEST_PROTOCOL)
    return 辭典
