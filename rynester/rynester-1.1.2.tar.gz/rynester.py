"""This is the "rynester.py" module, and it provides one function called
    print(lol) which prints lists that may or may not be include nested lists""" 

def print_lol(the_list):
    """This function checks each item in the list using isinstance BIF.
        If the list item happens to be a list, it recursively calls the print_lol function on that list item."""

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

            

