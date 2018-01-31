from .helpers import console
from . import server
from . import client_gui
from . import client_console


def main():
    console_params = console.args()
    if console_params.mode == 'server':
        server.run()
    elif console_params.mode == 'gui_client':
        client_gui.run()
    else:
        client_console.run()


if __name__ == "__main__":
    main()
