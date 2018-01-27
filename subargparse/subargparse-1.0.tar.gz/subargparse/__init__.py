def subparser_decorator():
    tree = {}

    def get_entry(t, *path):
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
        def wrapper_inner(func):
            set_entry(tree, func, path + (func.__name__,))
            return func

        return wrapper_inner

    def bind(self, parser):
        def configure_help(p, path):
            p.set_defaults(func=lambda x: parser.parse_args(reversed(path + ["-h"])))

        def configure_parser(d, p, path):
            configure_help(p, path)
            sps = p.add_subparsers(title='subcommands',
                                        description='valid subcommands')
            for k, v in d.items():
                if isinstance(v, dict):
                    lp = sps.add_parser(k)
                    configure_parser(v, lp, path + [k])
                else:
                    lp = sps.add_parser(k)
                    action = v(lp)
                    lp.set_defaults(func=action)

        def handle(self, args):
            args.func(args)
        parser.handle = handle.__get__(parser, parser.__class__)

        configure_parser(self.tree, parser, [])
    wrapper.tree = tree
    wrapper.bind = bind.__get__(wrapper, wrapper.__class__)
    return wrapper
