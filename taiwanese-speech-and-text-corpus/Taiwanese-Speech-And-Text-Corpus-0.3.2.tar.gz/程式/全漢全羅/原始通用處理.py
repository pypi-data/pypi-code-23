
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.文章粗胚 import 文章粗胚
from 臺灣言語工具.音標系統.閩南語.通用拼音音標 import 通用拼音音標


class 原始通用工具:
    音標錯誤表 = [
        ('niunn', 'niu'), ('min', 'bin'),
        ('miann', 'mia'), ('mong', 'bong'), ('ming', 'bing'),
        ('nq', 'ng'),
        ('ya', 'ia'),
    ]

    @classmethod
    def 處理做口語調臺羅(cls, 通用口語音標):
        新音標 = 通用口語音標.replace('_', '-').strip('-').replace(',', ' ').strip()
        新音標 = 文章粗胚.數字英文中央全加分字符號(新音標)
        for 錯, 著 in cls.音標錯誤表:
            新音標 = 新音標.replace(錯, 著)
        新音標 = 文章粗胚.建立物件語句前處理減號(通用拼音音標, 新音標)
        音標句物件 = 拆文分析器.建立句物件(新音標)
        return 音標句物件.轉音(通用拼音音標)
