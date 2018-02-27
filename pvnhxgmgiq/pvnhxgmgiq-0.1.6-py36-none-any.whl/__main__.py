# coding=utf-8
"""
Dummy
"""
import elib


def main():
    """
    Dummy
    """
    from pvnhxgmgiq import __version__
    print(__version__, type(__version__))
    elib.updater.Updater('132nd-etcher/hello_world', __version__, 'pvnhxgmgiq.exe').update()


if __name__ == '__main__':
    main()
