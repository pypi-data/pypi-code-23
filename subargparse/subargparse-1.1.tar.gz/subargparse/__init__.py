def subparser_decorator():
    '''
    Creates a custom subparser decorator
    :return: Decorator
    '''
    tree = {}

    def get_entry(t, *path):
        '''
        Gets the entry at the specified path in a tree
        :param t: Tree
        :param path: Entry path
        :return: Entry value
        '''
        if isinstance(path[0], list) or isinstance(path[0], tuple):
            path = path[0]
        entry = t
        for k in path:
            if k in entry:
                entry = entry[k]
            else:
                return None
        return entry

    def set_entry(t, v, *path):
        '''
        Sets an entry at the specified path in a tree
        :param t: Tree
        :param v: Entry value
        :param path: Entry Path
        :return: None
        '''
        if isinstance(path[0], list) or isinstance(path[0], tuple):
            path = path[0]
        entry = t
        for k in path[:-1]:
            if k in entry:
                entry = entry[k]
            else:
                entry[k] = {}
                entry = entry[k]

        entry[path[-1]] = v

    def wrapper(*path):
        '''
        Decorator wrapper function
        :param path: Subcommand path
        :return: Inner wrapper
        '''
        def wrapper_inner(func):
            '''
            Inner decorator wrapper function
            :param func: Subcommand function
            :return: The original function unchanged
            '''
            set_entry(tree, func, path + (func.__name__,))
            return func

        return wrapper_inner

    def bind(self, parser):
        '''
        Binds the subparser to an argparse parser
        :param self: subparser object
        :param parser: argparse parser
        :return: None
        '''
        def configure_help(p, path):
            '''
            Configures help for a partial command
            :param p: Parser
            :param path: Path
            :return: None
            '''
            p.set_defaults(func=lambda x: parser.parse_args(reversed(path + ["-h"])))

        def configure_parser(t, parser, path):
            '''
            Recursively configures subcommands
            :param t: Subcommand tree
            :param p: Parser
            :param path: Current path
            :return: None
            '''
            configure_help(parser, path)
            sps = parser.add_subparsers(title='subcommands',
                                        description='valid subcommands')
            for k, v in t.items():
                if isinstance(v, dict):
                    lp = sps.add_parser(k)
                    configure_parser(v, lp, path + [k])
                else:
                    lp = sps.add_parser(k)
                    action = v(lp)
                    lp.set_defaults(func=action)

        def handle(self, args):
            '''
            Handles an argument according to the correct subcommand
            :param self: argparse parser object
            :param args: Command arguments
            :return: Function result
            '''
            return args.func(args)
        parser.handle = handle.__get__(parser, parser.__class__)

        configure_parser(self.tree, parser, [])
    wrapper.tree = tree
    wrapper.bind = bind.__get__(wrapper, wrapper.__class__)
    return wrapper
