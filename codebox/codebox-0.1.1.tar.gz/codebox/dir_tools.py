import os


def list_files(path, recursive=False):
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            if dirnames and recursive:
                for d in dirnames:
                    list_files(os.path.join(dirpath, d))
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))


if __name__ == '__main__':
    for f in list_files('codebox'):
        print(f)
