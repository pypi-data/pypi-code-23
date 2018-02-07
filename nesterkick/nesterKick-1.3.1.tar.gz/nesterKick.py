import sys

def print_lol(the_list, indentation=False, level=0, fh=sys.stdout):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indentation, level+1, fh)
        else:
            if( indentation ):
                for tab_stop in range(level):
                    print ("\t", end=" ", file=fh)
            print(each_item, file=fh)