from argparse import ArgumentParser


def create_parser(usage):
    """
    Creates an argument parser from a condensed usage string in the format of:

    This is the program description

    :pos_arg_name int
        This is the help message
        which can span multiple lines
    :-o --optional_arg str default_value
        The type can be any valid python type
    :-eo --extra-option
        This adds args.extra_option as a bool
        which is False by default

    Args:
        usage (str): Usage string in the format described above
    Returns:
        ArgumentParser: parser object created from the described string
    """
    parser = ArgumentParser()
    add_to_parser(parser, usage)
    return parser


def add_to_parser(parser, usage):
    """
    Add arguments described in the usage string to the
    parser. View more details at the <create_parser> docs

    Args:
        parser (ArgumentParser): parser to add arguments to
        usage (str): Usage string in the format described above
    """
    usage = '\n' + usage
    first_line = [i for i in usage.split('\n') if i][0]
    indent = ' ' * (len(first_line) - len(first_line.lstrip(' ')))
    usage = usage.replace('\n' + indent, '\n')
    usage = usage.replace('\n...', '')

    defaults = {}
    description, *descriptors = usage.split('\n:')
    description = description.replace('\n', ' ').strip()
    if description:
        parser.description = description
    for descriptor in descriptors:
        try:
            options, *help = descriptor.split('\n')
            help = ' '.join(help).replace('    ', '')
            if options.count(' ') == 1:
                if options[0] == '-':
                    short, long = options.split(' ')
                    var_name = long.strip('-').replace('-', '_')
                    parser.add_argument(short, long, dest=var_name, action='store_true', help=help)
                    defaults[var_name] = False
                else:
                    short, typ = options.split(' ')
                    parser.add_argument(short, type=eval(typ), help=help)
            else:
                short, long, typ, default = options.split(' ')
                help += '. Default: ' + default
                default = '' if default == '-' else default
                parser.add_argument(short, long, type=eval(typ), default=default, help=help)
        except Exception as e:
            print(e.__class__.__name__ + ': ' + str(e))
            print('While parsing:')
            print(descriptor)
            exit(1)
