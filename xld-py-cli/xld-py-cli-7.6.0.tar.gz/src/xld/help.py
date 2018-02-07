# flake8: noqa
help_message = """
Usage:
     xld <connection-options> <command> [command-options]
     
Commands:
    apply           Apply a Deployfile to the XL Deploy repository.
    generate        Generate a Deployfile from the XL Deploy repository.
    help            Show help.
    version         Show version.
    deploy          Application version to an environment.

Connection Options:     
    --url           Location of the XL Deploy server (including port).
    --username      User name to use when authenticating with XL Deploy.
    --password      Password to use when authenticating with XL Deploy.

Command Options:
    --debug         Shows stacktrace if error
"""
