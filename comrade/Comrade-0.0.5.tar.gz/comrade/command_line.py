from __future__ import print_function, absolute_import
from .configuration import read_config, find_config
from .main_menu import MainMenu


def main():
    test_json = find_config()
    configuration = read_config(test_json)
    MainMenu(configuration).show()


if __name__ == "__main__":
    main()
