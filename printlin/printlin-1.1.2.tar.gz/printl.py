#Windows python3
#printl

#迭代打印列表 函数

import sys

def printL(the_list,indent=False,level=0,f=sys.stdout):
    ''' print list of list.

    4 argument: the_list,indent=False,level=0,f=sys.stdout .

        the_list        要打印或保存的列表,
        indent=False    默认不缩进,
        level=0         控制缩进tab数,
        f=sys.stdout    默认输出至屏幕
    '''
    for i in the_list:
        if isinstance(i,list):
            printL(i,indent,level+1,f)
        else:
            if indent:
                for j in range(level):
                    print('\t',end='',file=f)
            print(i,file=f)
