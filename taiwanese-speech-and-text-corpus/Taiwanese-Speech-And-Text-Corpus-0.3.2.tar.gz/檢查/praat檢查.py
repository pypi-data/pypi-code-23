from praatio.tgio import openTextgrid


class praat檢查:
    def __init__(self):
        self.錯誤 = []

    def 發生錯誤(self, 錯誤):
        self.錯誤.append(錯誤)

    def 錯誤資訊(self):
        return '\n'.join(self.錯誤)

    def 有錯誤無(self):
        return len(self.錯誤) != 0

    def 檢查聽拍(self, 聽拍資料):
        for 開始, 結束, 聽拍 in 聽拍資料:
            for 舊標仔 in ['[empty]', '[noise]', '[silence]', 'ATHL', ]:
                if 舊標仔 in 聽拍:
                    self.發生錯誤('語句{}-{}，有{}'.format(開始, 結束, 舊標仔))
            趨線數量 = 0
            for 字 in 聽拍:
                if 字 == '/':
                    趨線數量 += 1
            if 趨線數量 > 2:
                self.發生錯誤('語句{}-{}，趨線愛調整：{}'.format(開始, 結束, 聽拍))

    def 檢查語者(self, 聽拍資料, 語者資料):
        時間 = set()
        for 開始, 結束, _聽拍 in 聽拍資料:
            時間.add(開始)
            時間.add(結束)
        for 開始, _結束, _聽拍 in 語者資料:
            if 開始 not in 時間:
                self.發生錯誤('語者第{}秒的時間，佮聽拍無仝'.format(開始))

    def 檢查檔案(self, 檔名):
        try:
            聽拍資料 = self.提出聽拍資料(檔名)
        except KeyError:
            self.發生錯誤('TextGrid無Speech的Tier')
            return
        self.檢查聽拍(聽拍資料)
        try:
            語者資料 = self.提出語者資料(檔名)
        except KeyError:
            self.發生錯誤('TextGrid無Turns的Tier')
            return
        self.檢查語者(聽拍資料, 語者資料)

    def 提出聽拍資料(self, 檔名):
        return openTextgrid(檔名).tierDict["Speech"].entryList

    def 提出語者資料(self, 檔名):
        return openTextgrid(檔名).tierDict["Turns"].entryList
