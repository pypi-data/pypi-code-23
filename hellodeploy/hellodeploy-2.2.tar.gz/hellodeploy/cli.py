import os.path
import json
import sys

from hellodeploy.utils import register, upload, extract_options
from hellodeploy.settings import CRED_PATH, OPT_PATH

def main():
    credentials = os.path.exists(CRED_PATH)
    options = os.path.exists(OPT_PATH)

    if 'init' in sys.argv:
        f = open(OPT_PATH, 'w+')
        f.close()

    if options:
        data, options = extract_options()
    if credentials:
        f = open(CRED_PATH, 'r')
        token = f.read()
        if token[-1] == '\n':
            token = token[:-1]
        upload(token, data, options)
    else:
        token = register()
        if token[-1] == '\n':
            token = token[:-1]
        upload(token, data, options)

if __name__ == "__main__":
    main()
