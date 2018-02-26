"""This module encapsulates constant shell commands."""

class Commands:
    """This class holds many shell commands.

    You can use this class to access many constant shell commands.
    """

    cmd_echo = "echo hello"
    cmd_ipforward = "sysctl -w net.ipv4.ip_forward=1"
    cmd_check_key = "grep -q '{}' ~/.ssh/authorized_keys && echo $?"
    cmd_generate_ed25519_key = 'ssh-keygen -f {} -t ed25519 -N ""'
    cmd_start_client = "netconf -sniff"

class Paths:
    """This class holds all the paths.
    """

    config_file = "netconflib/config.ini"
    config_file_test = "tests/config.ini"