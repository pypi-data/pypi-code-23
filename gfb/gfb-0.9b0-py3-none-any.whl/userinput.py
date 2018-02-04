import readchar
import typing

def read_response(self, prompt: str=None) -> str:
    """
    reads a single character response from the user
    params:
        prompt: str optional prompt to display
    returns:
        the character read
    """
    if prompt:
        sys.stdout.write(prompt)
        sys.stdout.flush()
    ch = readchar.readchar()
    sys.stdout.write(ch)
    return ch
