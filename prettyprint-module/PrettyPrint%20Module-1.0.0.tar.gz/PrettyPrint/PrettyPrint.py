"""
Pretty print with indentation
"""
def prettyPrint(thelist, space=''):
    space = space + " "
    for each_item in thelist:
        if isinstance(each_item, list):
            prettyPrint(each_item, space)
        else:
            print("{}{}".format(space, each_item))

if __name__ == '__main__':
    print("hello!")
    # prettyPrint({1, 2, 3, "a", "hello",[ 4, 5, 6], 'guru', ["hello", 1 , 2, 4, ['a','e','i','o','u']]})
    prettyPrint(['1','2','3',["a","b","c",['a','e','i',"there!"],'end1'],"theSecond"])