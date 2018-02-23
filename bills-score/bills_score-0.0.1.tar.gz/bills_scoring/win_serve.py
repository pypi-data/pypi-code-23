from waitress import serve
from . import hug_api, settings
import fire


class WindowsServe:

    def server(self):
        serve(hug_api.__hug_wsgi__,
              listen="*:{}".format(settings.LOCAL_HTTPD_PORT))


def main():
    fire.Fire(WindowsServe)


if __name__ == '__main__':
    main()
