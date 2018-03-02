"""This module is used to Read and print contents of any nested lists"""

def listLooper(Carsu):

  'Iterate through the list recursively to print its contents'
  
  for u in Carsu :
    if isinstance(u,list):
        listLooper(u)
    else:
        print(u)