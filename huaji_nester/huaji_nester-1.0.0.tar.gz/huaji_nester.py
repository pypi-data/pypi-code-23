"""this is the huaji_nester.py module """

def print_lol(the_list):
    #the function ...
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
