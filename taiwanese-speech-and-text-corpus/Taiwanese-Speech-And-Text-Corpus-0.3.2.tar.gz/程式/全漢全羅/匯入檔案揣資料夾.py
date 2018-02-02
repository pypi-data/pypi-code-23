from os import walk
from os.path import basename, join


def 揣資料夾內的語料(來源json, 來源wav):
    wav路徑 = {}
    for 所在, _, 檔名陣列 in walk(來源wav):
        for 檔名 in 檔名陣列:
            if 'With_error' not in 所在 and 檔名.endswith('.wav'):
                資料夾 = basename(所在)
                定位 = (資料夾, 檔名[:-4])
                if 定位 in wav路徑:
                    raise RuntimeError('有仝款定位的資料：{}'.format(定位))
                wav路徑[(資料夾, 檔名[:-4])] = join(所在, 檔名)
    for 所在, _, 檔名陣列 in sorted(walk(來源json)):
        for 檔名 in sorted(檔名陣列):
            if 檔名.endswith('.json'):
                json檔名 = join(所在, 檔名)
                資料夾 = basename(所在)
                try:
                    wav原始對應 = (
                        檔名.split('|')[0]
                        .replace('&amp;', '&')
                    )
                    wav檔名 = wav路徑[(資料夾, wav原始對應)]
                except KeyError:
                    # 有問題
                    if (資料夾, wav原始對應) == ('Dream_State', '1103-230002'):
                        print((資料夾, wav原始對應))
                        pass
                    elif (資料夾, wav原始對應) == ('FTVN-1', '090522_B_FTVNt'):
                        yield json檔名, wav路徑[(資料夾, '090522_B_FTVN')]
                    elif (資料夾, wav原始對應) == ('FTVN-3', '20110713-zy'):
                        yield json檔名, wav路徑[(資料夾, '20110713-zy-1')]
                    elif (
                        (資料夾, wav原始對應) == ('Neighbor', '20121103_Neighbor-02')
                    ):
                        yield json檔名, wav路徑[(資料夾, '20121103_Neighbor')]
                    elif (資料夾, wav原始對應) == ('TW03', '_Chen Su Nian_0'):
                        yield json檔名, wav路徑[(資料夾, '_Chen_Su_Nian_0')]
                    else:
                        raise
                else:
                    yield json檔名, wav檔名
