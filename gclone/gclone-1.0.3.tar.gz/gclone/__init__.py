import argparse
import shutil
import subprocess
import sys
from .gclone import Gsearch, Gclone

def _maybe_do_clone(clone_url, *clone_args):
    if clone_url:
        assert isinstance(clone_url, str)
        print('> git clone {} {}'.format(clone_url, ' '.join(clone_args)))
        _git('clone', clone_url, *clone_args)

def _git(*args):
    return subprocess.run(['git'] + list(args))

def _get_input(msg):
    try:
        return input(msg)
    except KeyboardInterrupt:
        print('Abort.')
        exit()

def _fit_term_width(lines):
    if lines is None:
        return lines
    """Shorten each line of a string to the width of the terminal."""
    term_cols = shutil.get_terminal_size((80, 20)).columns
    new_lines = []
    for line in lines.splitlines():
        line = (line[:term_cols - 3] + '...') if len(line) > term_cols else line
        new_lines.append(line)
    return '\n'.join(new_lines)

def _prepare_args(args):
    num = len(args)
    new_args = []
    next_arg = None
    for i in range(num):
        arg = args[i]
        if i < num - 1 and arg.startswith('--') and '=' not in arg:
            next_arg = args[i + 1]
            new_args.append('{}={}'.format(arg, next_arg))
        elif arg is not next_arg:
            new_args.append(arg)
    return new_args

def parseopts(args):
    parser = argparse.ArgumentParser(prog='gclone',
            usage='%(prog)s [options] repo [dir]')
    # repo
    parser.add_argument('repo', help='keyword or repo name')

    # --sort
    sort_default = Gsearch.SORT_CHOICES[0]
    sort_help = "default is {}".format(sort_default)
    parser.add_argument('--sort', choices=Gsearch.SORT_CHOICES,
            default=sort_default, help=sort_help)

    # --order
    order_default = Gsearch.ORDER_CHOICES[0]
    order_help = "default is {}".format(order_default)
    parser.add_argument('--order', choices=Gsearch.ORDER_CHOICES,
            default=order_default, help=order_help)
    # --limit
    parser.add_argument('--limit', type=int, default=Gsearch.LIMIT_DEFAULT,
            help='max search results, ' \
                    'default is {}'.format(Gsearch.LIMIT_DEFAULT))

    parsed_args = parser.parse_known_args(_prepare_args(args))
    known_args = parsed_args[0]
    unknown_args = parsed_args[1]
    return (known_args, unknown_args)

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    known_args, clone_args = parseopts(args)
    keyword = known_args.repo

    search_args = dict(known_args.__dict__)
    del search_args['repo']
    gsearch = Gsearch()
    search_results = gsearch.search(keyword, **search_args)

    gclone = Gclone(keyword, search_results)
    output = _fit_term_width(gclone.get_output())
    if gclone.needs_input():
        user_input = _get_input(output) # Prints output
        try:
            gclone.handle_input(user_input)
        except (IndexError, KeyError, TypeError):
            print('Invalid input.')
    elif output is not None:
        print(output)

    _maybe_do_clone(gclone.get_clone_url(), *clone_args)

if __name__ == '__main__':
    main()
