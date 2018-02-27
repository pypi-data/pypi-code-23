#!/usr/bin/env python
import os
import sys


def main(args=None):
    """The main routine."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pipinator.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    command = [sys.argv[0], 'migrate', '--noinput']
    execute_from_command_line(command)

    command = [sys.argv[0], 'runserver', '0.0.0.0:8000']
    execute_from_command_line(command)


if __name__ == "__main__":
    main()