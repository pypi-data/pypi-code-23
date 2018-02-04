import sys
import readchar
import typing

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
