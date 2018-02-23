from waitress import serve
from . import hug_api, settings, user_schema_db
import fire


class WindowsServe:

    def server(self):
        serve(hug_api.__hug_wsgi__,
              listen="*:{}".format(settings.LOCAL_HTTPD_PORT))


def check_if_db_exists():
    import os
    db_path = os.path.join(user_schema_db.file_path, settings.DB_NAME)
    if not os.path.isfile(db_path):
        # Create database
        data_engine = user_schema_db.UserWrapper()
        data_engine.create_db()

        # Create Initial User
        data_engine.create_user(
                "user",
                "LOSASASA",
                "a12-a23-a34",
        )


def main():
    check_if_db_exists()
    fire.Fire(WindowsServe)


if __name__ == '__main__':
    main()
