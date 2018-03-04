from __future__ import print_function, absolute_import
from .configuration import read_config
from .main_menu import MainMenu
from os import path


def main():
    test_json = path.join(path.dirname(
        path.realpath(__file__)), "../configs/test_config.json")
    configuration = read_config(test_json)
    MainMenu(configuration).show()


if __name__ == "__main__":
    main()
