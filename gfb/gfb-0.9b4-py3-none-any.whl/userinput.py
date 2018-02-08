import sys
import readchar
import typing
import getpass

def read_response(prompt: str=None) -> str:
    """
    reads a single character response from the user
    params:
        prompt: str optional prompt to display
    returns:
        the character read
    """
    if prompt:
        print(prompt, end='', flush=True)
    ch = readchar.readchar()
    print("{0}\n".format(ch))
    return ch

def prompt(prompt: str, secure: bool=False):
    """
    Reads a line of input from the user
    params:
        prompt: input prompt
        secure: read with getpass
    returns:
        the string entered
    """
    result = ""
    try:
        if secure:
            result = getpass.getpass(prompt)
        else:
            result = input(prompt)
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        return result
