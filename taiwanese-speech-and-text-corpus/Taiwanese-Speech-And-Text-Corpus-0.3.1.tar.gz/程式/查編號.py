from 程式.編號對照表 import 編號對照


class 查編號:
    def __init__(self):
        self.編號資訊 = 編號對照.讀編號資訊()
        self.檔名資訊 = 編號對照.讀檔名資訊()

    def 資訊(self, 資料夾名, 音檔名, 聽拍名, 開始時間, 結束時間):
        try:
            return self.編號資訊[
                (
                    self.檔名資訊[(資料夾名, 音檔名, 聽拍名)],
                    開始時間,
                    結束時間
                )
            ]
        except KeyError:
            return {
                '舊編號': None,
                '新編號': None,
                '有揀出來無': False,
            }
