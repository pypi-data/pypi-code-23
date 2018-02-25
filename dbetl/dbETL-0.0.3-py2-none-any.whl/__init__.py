from .pyAPI import api
import sys

if __name__=='__main__':
    ID, start, end = sys.argv[1:]
    print ID, start, end
    api(ID, start, end)