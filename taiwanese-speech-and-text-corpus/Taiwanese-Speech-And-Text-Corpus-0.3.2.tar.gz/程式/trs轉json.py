import re


class trs轉json:

    @classmethod
    def trs檔案(cls, trs):
        with open(trs) as 檔案:
            return cls.trs字串(檔案.read())

    @classmethod
    def trs字串(cls, trs):
        語者 = {}
        資料 = []
        這馬資料 = ''
        這馬時間 = None
        for 一逝 in trs.split('\n'):
            句 = 一逝.strip()
            if 句 == '':
                這馬資料 = 這馬資料 + ' '
            elif 句.startswith('<Speaker '):
                編號 = re.search(r' id="([^"]*)" ', 句).group(1)
                名 = re.search(r' name="([^"]*)" ', 句).group(1)
                語者[編號] = 名
            elif 句.startswith('<Turn '):
                try:
                    編號 = re.search(r' speaker="([^"]*)" ', 句).group(1)
                    這馬語者 = 語者[編號]
                except AttributeError:
                    這馬語者 = '無註明'
                結束時間 = re.search(r' endTime="([^"]*)"', 句).group(1)
            elif 句.startswith('</Turn>'):
                頂一个時間 = 這馬時間
                這馬時間 = 結束時間
                這馬資料 = 這馬資料.strip()
                if len(這馬資料) > 0:
                    if 頂一个時間 is None:
                        raise RuntimeError('trs有問題，無Sync時間煞有文本')
                    # 處理換逝的問題
                    上尾資料 = 這馬資料.replace(' -', '-')
                    資料.append({
                        '開始時間': 頂一个時間,
                        '結束時間': 這馬時間,
                        '語者': 這馬語者,
                        'trs聽拍': 上尾資料,
                    })
                    這馬資料 = ''
            elif 句.startswith('<Sync'):
                頂一个時間 = 這馬時間
                這馬時間 = 句.split('"')[1]
                這馬資料 = 這馬資料.strip()
                if len(這馬資料) > 0:
                    if 頂一个時間 is None:
                        raise RuntimeError('trs有問題，無Sync時間煞有文本')
                    # 處理換逝的問題
                    上尾資料 = 這馬資料.replace(' -', '-')
                    資料.append({
                        '開始時間': 頂一个時間,
                        '結束時間': 這馬時間,
                        '語者': 這馬語者,
                        'trs聽拍': 上尾資料,
                    })
                    這馬資料 = ''
            elif 句.startswith('<'):
                這馬資料 = 這馬資料 + ' '
            elif 句.startswith('\ufeff'):
                這馬資料 = 這馬資料 + ' '
            else:
                這馬資料 = 這馬資料 + 句
        if len(這馬資料.strip()) > 0:
            raise RuntimeError('trs有問題，上尾的文本無Sync時間')
        return 資料
