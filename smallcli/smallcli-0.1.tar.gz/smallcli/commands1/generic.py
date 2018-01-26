from smallcli.commands.base import Command


class exit1(Command):
    description = "Exit from the CLI"
    details = '''
    Exit from the CLI
    Arguments: None
    '''

    def __call__(self):
        raise EOFError


class substract(Command):
    description = "add  - add two numbers ,return result"
    details = '''
    Add two numbers
    Args: a  b
    type: interger
    return: result
    Example:   add 10 20
    '''

    def __call__(self):
        return "Hello Command Returned"


class delete(Command):
    description = "Test command"
    details = '''
    Add two numbers
    Args: a  b
    type: interger
    return: result
    Example:   add 10 20
    '''
    def __call__(self):
        return "Test Command Executed"
"""
class help(Command):
    description = "help command"
    details = '''
    Help Command
    Args: None
    '''

    def __call__(self):
        return "help Command Executed"
"""