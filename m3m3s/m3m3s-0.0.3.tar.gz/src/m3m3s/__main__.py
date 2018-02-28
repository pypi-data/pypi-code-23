import argparse
from . import decapitator

# at the module level, we'll have to make our own parser


def build_module_argparser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    parser_decapitator = subparsers.add_parser('decapitator')
    decapitator.add_args_to_parser(parser_decapitator)
    parser_decapitator.set_defaults(func=decapitator.main)

    subparsers.required = True
    subparsers.dest = "command"

    return parser


def main():
    args = build_module_argparser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
