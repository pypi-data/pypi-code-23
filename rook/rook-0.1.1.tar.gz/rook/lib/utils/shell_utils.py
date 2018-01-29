import socket
from subprocess import Popen, PIPE


class ShellUtils(object):
    """
    Utilities to run classic shell commands
    currently bash (unix) oriented
    """

    class ParsingException(Exception):
        pass

    @staticmethod
    def exec_cmd(cmd):
        """
        :param cmd: comamnd-line
        :return: (stdout, stderr) tuple
        """
        return Popen(cmd.split(" "), stdout=PIPE, stderr=PIPE).communicate()

    @classmethod
    def get_pid_of_process_name(cls, name):
        try:
            return int(cls.exec_cmd("pidof %s" % name)[0])
        except ValueError:
            return None

    @classmethod
    def get_process_connections(cls, process_name, only_listening=False):
        """
        Netstat parser
        """
        import psutil
        res = []
        pid = cls.get_pid_of_process_name(process_name)
        for connection in psutil.net_connections():
            if connection.pid == pid:
                if not only_listening or\
                                connection.status == "LISTEN" or\
                                connection.type != socket.SOCK_STREAM:
                    res.append(connection)
        return res


