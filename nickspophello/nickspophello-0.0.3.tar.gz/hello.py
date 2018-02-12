import sys

__version__ = '0.0.3'


def hello(name='World'):
    """
    Return a greeting for the given name
    """
    return 'Hello, {}'.format(name)


def main():
    args = sys.argv[1:]
    name = ' '.join(args)
    if name:
        print(hello(name))
    else:
        print(hello())


if __name__ == '__main__':
    main()
