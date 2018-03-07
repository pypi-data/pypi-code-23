# coding =utf-8
# author:黑亮之星(qq:410445759)
# info: 

def item(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
           item(each_item)
        else:
            print(each_item)
