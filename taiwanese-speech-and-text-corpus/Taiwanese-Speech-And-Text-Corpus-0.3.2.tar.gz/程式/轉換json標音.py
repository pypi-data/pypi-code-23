#!python
import json
from os import makedirs
from os.path import isdir, join, basename
from posix import listdir

from django.conf import settings


from 程式.提出通用音標 import 提出通用音標
from 程式.查編號 import 查編號
from 臺灣言語工具.解析整理.拆文分析器 import 拆文分析器
from 臺灣言語工具.解析整理.文章粗胚 import 文章粗胚
from 程式.全漢全羅.揣全漢全羅 import 揣全漢全羅
from 程式.全漢全羅.原始通用處理 import 原始通用工具


class 轉json():
    def __init__(self):
        self.全漢全羅 = 揣全漢全羅()
        self.查編號 = 查編號()
        self.第幾个檔 = 0

    def 轉規个資料夾(self,  來源, 目標, 數量):
        makedirs(目標, exist_ok=True)
        for 檔名 in sorted(listdir(來源)):
            if self.第幾个檔 == 數量:
                break
            來源檔案 = join(來源, 檔名)
            目標檔案 = join(目標, 檔名)
            if isdir(來源檔案):
                self.轉規个資料夾(來源檔案, 目標檔案, 數量)
            elif 檔名.endswith('json'):
                print('紲落來來轉 {}'.format(檔名))
                with open(來源檔案) as 原本json來源:
                    資料 = json.load(原本json來源)
                for 第幾筆, 一筆資料 in enumerate(資料):
                    if 第幾筆 % 100 == 0:
                        print('第{}筆'.format(第幾筆))
                    self.更新(basename(來源), 檔名, 一筆資料)
                with open(目標檔案, 'w') as 寫檔:
                    json.dump(
                        資料,
                        寫檔,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True
                    )
                self.第幾个檔 += 1

    def 更新(self, 資料夾名,  聽拍檔名, 一筆資料):
        原始通用 = 提出通用音標.揣音標(一筆資料['trs聽拍'])
        一筆資料['原始通用'] = 原始通用

        口語調臺羅物件 = 原始通用工具.處理做口語調臺羅(原始通用)
        轉出來句物件 = self.全漢全羅.變調臺羅轉本調臺羅(口語調臺羅物件)
        本調句物件 = 拆文分析器.分詞句物件(轉出來句物件.看分詞().replace('-｜-', ''))
        一筆資料['漢字'] = 文章粗胚.數字英文中央全加分字符號(本調句物件.看型())
        一筆資料['臺羅'] = 本調句物件.看音()
        一筆資料['分詞'] = 本調句物件.看分詞()

        口語調句物件 = 轉出來句物件
        for 口語字, 臺羅字 in zip(
            口語調句物件.篩出字物件(), 口語調臺羅物件.篩出字物件()
        ):
            口語字.音 = 臺羅字.型
        一筆資料['口語調臺羅'] = (
            拆文分析器.分詞句物件(
                口語調句物件.看分詞().replace('-｜-', '')
            )
            .看音()
        )

        一筆資料.update(
            self.查編號.資訊(
                資料夾名, None, 聽拍檔名,
                一筆資料['開始時間'], 一筆資料['結束時間']
            )

        )


def 來轉羅馬字(數量=1000000):
    轉json().轉規个資料夾(
        join(settings.BASE_DIR, 'Finished-Json'),
        join(settings.BASE_DIR, 'TL-Json'),
        數量
    )


if __name__ == '__main__':
    來轉羅馬字()
