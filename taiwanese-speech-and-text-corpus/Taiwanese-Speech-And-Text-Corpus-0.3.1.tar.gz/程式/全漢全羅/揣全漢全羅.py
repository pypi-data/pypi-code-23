import gzip
from os.path import isfile
import pickle
from 臺灣言語工具.斷詞.拄好長度辭典揣詞 import 拄好長度辭典揣詞
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.語言模型.KenLM語言模型 import KenLM語言模型
from 臺灣言語工具.斷詞.語言模型揀集內組 import 語言模型揀集內組
from 程式.全漢全羅.做辭典 import 做
from 程式.全漢全羅.語料路徑 import 語料路徑
from 程式.全漢全羅.做辭典 import 漢字本調分開符號


class 揣全漢全羅:

    def __init__(self):
        if not isfile(語料路徑.斷詞典()) or not isfile(語料路徑.斷詞語言模型()):
            self.口語辭典 = 做()
        else:
            with gzip.open(語料路徑.斷詞典(), 'rb') as f:
                self.口語辭典 = pickle.load(f)
        self.語言模型 = KenLM語言模型(語料路徑.斷詞語言模型())

    def 變調臺羅轉本調臺羅(self, 變調句物件):
        接起來句物件 = 拆文分析器.建立句物件('')
        for 詞 in 變調句物件.網出詞物件():
            揣詞結果 = 拄好長度辭典揣詞.揣詞(self.口語辭典, 詞)
            揣著句物件 = 揣詞結果
            接起來句物件.內底集.extend(揣著句物件.內底集)
        for 集物件 in 接起來句物件.內底集:
            for 組物件 in 集物件.內底組:
                for 字物件 in 組物件.篩出字物件():
                    if 字物件.型 == '-':
                        字物件.音 = '-'
                    else:
                        try:
                            字物件.型, 字物件.音 = 字物件.型.split(漢字本調分開符號)
                        except ValueError:
                            # 辭典無這音
                            # print('{} 無佇語料出現'.format(字物件))
                            字物件.音 = 字物件.型
        結果 = 語言模型揀集內組.揀(self.語言模型, 接起來句物件)
        return 結果
