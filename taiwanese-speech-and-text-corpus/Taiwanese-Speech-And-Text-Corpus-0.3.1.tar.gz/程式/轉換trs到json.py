#!python
import json
from os import makedirs
from os.path import isdir, join, dirname
from posix import listdir
import re

from django.conf import settings
from 程式.trs轉json import trs轉json


def 轉規个資料夾(來源, 目標):
    makedirs(目標, exist_ok=True)
    for 檔名 in listdir(來源):
        來源檔案 = join(來源, 檔名)
        目檔檔案 = join(目標, 檔名)
        if isdir(來源檔案):
            轉規个資料夾(來源檔案, 目檔檔案)
        elif 檔名.endswith('trs'):
            with open(來源檔案) as 原本trs來源:
                資料 = 原本trs來源.read()
                audio_filename = re.search(
                    r'audio_filename="([^"]+)"', 資料
                ).group(1)
                version = re.search(r'version="([^\."]+)"', 資料).group(1)
                version_date = re.search(
                    r'version_date="([^"]+)"', 資料
                ).group(1)
            with open(join(
                目標,
                '{}|{}|{}|{}.json'.format(
                    audio_filename, version, version_date, 檔名[:-4]
                )
            ), 'w') as 寫檔:
                try:
                    print(
                        json.dumps(
                            trs轉json.trs檔案(來源檔案),
                            ensure_ascii=False,
                            indent=2,
                            sort_keys=True
                        ),
                        file=寫檔
                    )
                except Exception as 錯誤:
                    print(來源檔案, 錯誤)
#                     raise


def 來做json():
    專案目錄 = dirname(dirname(__file__))
    轉規个資料夾(
        join(專案目錄, 'Finished'),
        join(settings.BASE_DIR, 'Finished-Json')
    )


if __name__ == '__main__':
    來做json()
