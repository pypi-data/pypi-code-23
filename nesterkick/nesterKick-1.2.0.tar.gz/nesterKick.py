def print_lol(the_list, indentation=False, level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indentation, level+1)
        else:
            if( indentation ):
                for tab_stop in range(level):
                    print ("\t", end=" ")
            print(each_item)

cast = ["sdf", "sdaf", ["sadf", "asdf"]]
print_lol(cast, True, 3)