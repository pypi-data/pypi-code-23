import json
from os.path import dirname, abspath, join


class 編號對照:
    語料所在 = join(dirname(abspath(__file__)), '..', '編號資訊')

    @classmethod
    def 讀舊編號(cls):
        return cls._讀檔('舊segments')

    @classmethod
    def 讀新編號(cls):
        return cls._讀檔('新segments')

    @classmethod
    def 讀有揀出來用無(cls):
        return set(cls._讀檔('新train_nodev的segments').keys())

    @classmethod
    def 讀編號資訊(cls):
        編號資訊 = {}
        舊編號 = cls.讀舊編號()
        新編號 = cls.讀新編號()
        有揀出來用無 = cls.讀有揀出來用無()
        for 編號, 舊名 in sorted(舊編號.items()):
            編號資訊[編號] = {
                '舊編號': 舊名,
                '新編號': None,
                '有揀出來無': False,
            }
        for 編號, 新名 in sorted(新編號.items()):
            try:
                編號資訊[編號].update({
                    '新編號': 新名,
                    '有揀出來無': 編號 in 有揀出來用無,
                })
            except KeyError:
                編號資訊[編號] = {
                    '舊編號': None,
                    '新編號': 新名,
                    '有揀出來無': 編號 in 有揀出來用無,
                }
        return 編號資訊

    @classmethod
    def 讀檔名資訊(cls):
        檔名資訊 = {}
        with open(join(cls.語料所在, '檔名編號對應.json')) as 檔案:
            for 資料 in json.load(檔案):
                檔名資訊[
                    (資料['資料夾名'], 資料['音檔名'], 資料['聽拍名'])
                ] = int(資料['編號'])
                檔名資訊[
                    (資料['資料夾名'], None, 資料['聽拍名'])
                ] = int(資料['編號'])
        return 檔名資訊

    @classmethod
    def _讀檔(cls, 檔名):
        資料 = {}
        with open(join(cls.語料所在, 檔名)) as 檔案:
            for 一逝 in 檔案.readlines():
                if len(一逝.strip()) > 0:
                    語者名, 檔案名, 開始時間, 結束時間 = 一逝.split()
                    if not 檔案名.startswith('tong'):
                        raise RuntimeError('{} 無合格式'.format(檔名))
                    檔案編號 = int(檔案名[4:]) + 1
                    資料[(檔案編號, 開始時間, 結束時間)] = 語者名
        return 資料
