"""
The world's most awesome hello world module.
"""

import sys

__version__ = '0.0.1'

def hello(name='World'):
  """return a greeting for the given name"""
  return 'Hello, {}'.format(name)

def main():
  """reads input from the args passed into the scripts and printsthe output to stdout"""
  args = sys.argv[1:]
  name = ' '.join(args)
  if name:
    print(hello(name))
  else:
    print(hello())

if __name__ == '__main__':
  main()