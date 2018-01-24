import os.path
import json
from utils import register, upload, extract_options
import sys


def main():
    credentials = os.path.exists('.credentials')
    options = os.path.exists('.options')

    if 'init' in sys.argv:
        f = open('.options', 'w+')
        f.close()

    if credentials:
        f = open('.credentials', 'r')
        token = f.read()
        if token[-1] == '\n':
            token = token[:-1]
        data, options = extract_options()
        upload(token, data, options)
    else:
        token = register()
        if token[-1] == '\n':
            token = token[:-1]
        data, options = extract_options()
        upload(token, data, options)

if __name__ == "__main__":
    main()
