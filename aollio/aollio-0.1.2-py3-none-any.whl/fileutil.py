"""
File IO Util.
"""


def write_file(path, content: str, bytes_mode=False):
    if bytes_mode:
        content = bytes(content)
    else:
        content = str(content)
    mode = 'bw' if bytes_mode else 'w'
    with open(path, mode) as out:
        out.write(content)
