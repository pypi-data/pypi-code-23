from .pyAPI import api
import sys

def main():
    ID, start, end = sys.argv[1:]
    print ID, start, end
    api(ID, start, end)
    
    
def preset():
    import os
    os.system("dbETL 2 1 50 & dbETL 3 1 50 & dbETL 8 1 50 & dbETL 9 1 50 &")
