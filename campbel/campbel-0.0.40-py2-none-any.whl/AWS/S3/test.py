# -*- coding: utf-8 -*-

from boto.s3.connection import S3Connection
from boto.s3.key import Key


# S3Connection('アクセスキーの文字列', 'シークレットアクセスキーの文字列')
conn = S3Connection(
            'AKIAIUWJ5KW3QBKLMW3A',
            'alg9nIlBliiEvma6HDO/Wie96w73/gTHwsxK1NZ9')

bucket = conn.get_bucket('campbel2525')

# コンテンツを列挙する
# print list(bucket)
# print bucket.get_all_keys()

# フォルダのファイル一覧
for key in bucket.list(prefix='sotuken/results/tokyo_1/01_01'):
    print(key.name, key.size, key.last_modified)

# コンテンツを削除する
k = bucket.get_key('sotuken/results/tokyo_1/01_01')
k.delete()
# 空のディレクトリ作成
# k = Key(bucket)
# for month in range(1, 13):
#     for mode in ['01', '02', '03']:
#         print '{0:02d}'.format(month)+'_'+mode
#
#         k.key = 'sotuken/results/tokyo_1/'+'{0:02d}'.format(month)+'_'+mode+'/'
#         k.set_contents_from_string('')

# ファイツの保存
# f = Key(bucket)
# # 保存するファイル名。s3側
# f.key = 'test_folder/test1.mp4'
# # 保存するもの。自分側のファイル
# f.set_contents_from_filename('test3.txt')


# # ファイツの保存
# f = Key(bucket)
# # 保存するファイル名。s3側
# f.key = 'sotuken/results/tokyo_1/01_01/'
# # 保存するもの。自分側のファイル
# fout = open('/Volumes/microSd/downloads/', 'w')
# f.get_file(fout)








#
