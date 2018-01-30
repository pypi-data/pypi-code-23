import click

MINVALUE=0
MAXVALUE=11263

def decrypt(data, key, outfile):
    for char in data:
        code = ord(char) - key

        ok = False
        while not ok:
            ok = True
            if code < MINVALUE:
                code += MAXVALUE
                ok = False
            if code > MAXVALUE:
                code -= MAXVALUE
                ok = False

        outfile.write(chr(code))
        #print(code)
        #print(chr(code))
        #print(chr(ord(char) - key), end='')


def encrypt(data, key, outfile):
    for char in data:
        code = ord(char) + key

        ok = False
        while not ok:
            ok = True
            if code < MINVALUE:
                code += MAXVALUE
                ok = False
            if code > MAXVALUE:
                code -= MAXVALUE
                ok = False

        outfile.write(chr(code))
        #print(code)
        #print(chr(code))
        #print(chr(ord(char) + key), end='')


@click.command()
@click.option('-k', 'key', default=1, help='Key to use (Default: 1)')
@click.option('-d', 'do_decrypt', is_flag=True, default=False, help='Decode instead of decode')
@click.option('-o', 'outfile', type=click.File('w'), default='-', help='Output file (default: stdout)')
@click.argument('f', type=click.File('r'), default='-')
def cmd_caesar(f, key, do_decrypt, outfile):
    """Caesar Cypher"""

    data = f.read()

    if not data:
        print("Empty file or string!")
        return 1

    if do_decrypt:
        decrypt(data, key, outfile)
    else:
        encrypt(data, key, outfile)


if __name__ == '__main__':
    cmd_caesar()

