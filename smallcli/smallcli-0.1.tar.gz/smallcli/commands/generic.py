from smallcli.commands.base import Command
from smallcli.resources.ssh import ssh
import sys

class exit(Command):
    description = "Exit from the CLI"
    details = '''
    Exit from the CLI
    Arguments: None
    '''

    def __call__(self, args):
        sys.exit()


class add(Command):
    description = "Adds two integer numbers"
    details = '''
    Adds two integer numbers and return the result.
    Args: a  b
    type: interger
    return: result
    Example:  add 10 20
    '''

    def __call__(self, args):
        result = 0
        for item in args:
            result += int(item)
        return "Result " + str(result)


class test(Command):
    description = "Test command"
    details = '''
    Add two numbers
    Args: a  b
    type: interger
    return: result
    Example:   add 10 20
    '''

    def __call__(self, args):
        return "Test Command Executed with args " + str(args)


class runInRemoteServer(Command):
    description = "Execute the script in Remote Server"
    details = '''
    Copy a script file in the remote server and run the script file(application)
    Args: <serverip>  <username> <keyfile>  <filename>
    return: pid
    Example:   runInRemoteServer 10.1.1.5 root  /home/suresh/test_key.rsa testpython.py
    '''

    def validate(self, args):
        return True


    def __call__(self, args):
        if self.validate(args) is True:
            ssh1 = ssh(ip=args[0],key=args[2],user=args[1])
            ssh1.scp_put(src=args[3],dst="/tmp/runner.py")
            result = ssh1.run_cmd(command="./tmp/runner.py")
            return result
        else:
            return "ERROR: Invalid Arguments \n" + description + "\n" + details
