# -*- coding: UTF-8 -*-
import os


def rename(file_path, file_prefix):
    """
    批量修改文件夹里的文件名，前缀 + 递增整数
    :param file_path: 文件夹路径
    :param file_prefix: 修改后的文件名前缀
    """
    file_list = os.listdir(file_path)

    i = 0
    for file in file_list:
        ext = file.split('.')[-1].lower()
        old_path = os.path.join(file_path, file)
        new_name = file_prefix + str(i + 1) + '.' + ext
        new_path = os.path.join(file_path, new_name)
        if os.path.exists(new_path):
            new_path = os.path.join(file_path, '_' + new_name)
            os.rename(old_path, new_path)
        else:
            os.rename(old_path, new_path)
        print(old_path, '======>', new_path)
        i += 1


def main():
    prefix = 'longfei'  # 修改后的文件名前缀
    path = 'D:\\PyProjects\\auto_identify\\pictures\\dataset\\%s\\' % prefix  # 文件夹路径
    rename(path, prefix)


if __name__ == '__main__':
    main()
    quit()
