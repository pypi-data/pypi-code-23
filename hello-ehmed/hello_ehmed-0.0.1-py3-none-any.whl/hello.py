"""
The most awesome hello in the world
"""
import sys


__version__ = '0.0.1'


def hello(name='World!'):
    """
    Return a greeting for the given name.
    """
    return f'Hello, {name}'


def main():
    """
    Read input from the args passed
    into the script and prints the output to stdout
    """
    args = sys.argv[1:]
    name = ' '.join(args)
    if name:
        print(hello(name))
    else:
        print(hello())


if __name__ == '__main__':
    main()
