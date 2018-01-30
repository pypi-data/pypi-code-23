import click

from_char = {
    'a': '._',
    'b': '_...',
    'c': '_._.',
    'd': '_..',
    'e': '.',
    'f': '.._.',
    'g': '__.',
    'h': '....',
    'i': '..',
    'j': '.___',
    'k': '_._',
    'l': '._..',
    'm': '__',
    'n': '_.',
    'o': '___',
    'p': '.__.',
    'q': '__._',
    'r': '._.',
    's': '...',
    't': '_',
    'u': '.._',
    'v': '..._',
    'w': '.__',
    'x': '_.._',
    'y': '_.__',
    'z': '__..',
    '1': '.____',
    '2': '..___',
    '3': '...__',
    '4': '...._',
    '5': '.....',
    '6': '_....',
    '7': '__...',
    '8': '___..',
    '9': '____.',
    '0': '_____',
}

# invert the from_char dict
to_char = { v: k for k, v in from_char.items() }

def decode(data):
    for code in data.split('\n'):
        xlated = to_char.get(code, '')
        if xlated:
            print(xlated)


def encode(data):
    for character in data:
        xlated = from_char.get(character.lower(), '')
        if xlated:
            print(xlated)


@click.command()
@click.option('-d', 'do_decode', is_flag=True, default=False, help='Decode instead of decode')
@click.argument('f', type=click.File('r'), default='-')
def cmd_morse(f, do_decode):
    """Morse"""

    data = f.read()

    if not data:
        print("Empty file or string!")
        return 1

    if do_decode:
        decode(data)
    else:
        encode(data)




if __name__ == '__main__':
    cmd_morse()

