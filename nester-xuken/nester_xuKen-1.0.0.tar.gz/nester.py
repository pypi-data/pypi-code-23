# !/usr/bin/python
# Filename:nester.py

def prinit_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            prinit_lol(each_item)
        else:
            print(each_item)