# -*- coding: utf-8 -*-
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os
class S3():

    def __init__(self, access_key, secret_access_key, bucket_name):
        # self.access_key = access_key
        # self.secret_access_key = secret_access_key

        # S3Connection('アクセスキーの文字列', 'シークレットアクセスキーの文字列')
        conn = S3Connection(access_key,secret_access_key)
        self.bucket = conn.get_bucket(bucket_name)

    # コンテンツを削除する
    def deleteFile(self, key_name):
        k = self.bucket.get_key(key_name)
        k.delete()

    # s3に空のディレクトリ作成
    def createDir(self, dir_name):
        k = Key(bucket)
        k.key = dir_name
        k.set_contents_from_string('')

    # コンテンツを列挙する
    def getBucketList(self):
        return list(bucket)

    # コンテンツを列挙する
    def getDirList(self, dir_name):
        return list(dir_name)

    # バケットを返す。何かに使いたい時のため。
    def getBucket(self):
        return self.bucket

    def getKeyNameList(self, prefix):
        key_name = []
        for key in self.bucket.list(prefix=prefix):
            key_name.append(key.name)
        return key_name

    # ファイルのアップロード
    def uploadFileToS3(self, local_file, s3_file):
        # ファイツの保存
        f = Key(self.bucket)
        # 保存するファイル名。s3側
        f.key = s3_file
        # 保存するもの。自分側のファイル
        f.set_contents_from_filename(local_file)

    # local内のフォルダン中のファイル全部アップロード
    def uploadFilesToS3(self, local_dir, s3_dir):
        files = os.listdir(local_dir)

        for file_name in files:
            if os.path.isfile(local_dir+file_name):
                # print local_dir+file_name
                self.uploadFileToS3(local_dir+file_name, s3_dir+file_name)

    # 1つのファイルをダウンロード
    # key_name:campbel2525/ 以降のパス
    def downloadFileFromS3(self, local_file, s3_file):
        # dir名,ファイル名の取得
        dir_path, file_name = os.path.split(local_file)

        # なければ作る
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        # ファイツの保存
        k = Key(self.bucket)
        # 保存するファイル名。s3側
        k.key = s3_file
        # print local_save_path
        # exit()
        #  保存するもの。自分側のファイル
        fout = open(local_file, 'w')
        k.get_file(fout)

    # s3フォルダ内のファイル全部取得
    def downloadFilesFromS3(self, local_dir, s3_dir):
        # なければ作る
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # s3のフォルダ内のファイルのフルパス全取得
        key_name_list = self.getKeyNameList(s3_dir)

        # 1つ1つダウンロードして行く
        for key_name in key_name_list:
            # ファイル名だけ欲しい
            file_name = key_name.split('/')
            file_name = file_name[len(file_name)-1]

            if file_name != '':
                self.downloadFileFromS3(local_dir+file_name, s3_dir+file_name)







    #
