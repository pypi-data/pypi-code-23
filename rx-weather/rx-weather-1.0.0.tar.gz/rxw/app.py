import argparse
from rxw.openweathermap import CurrentConditions
from rxw._version import __version__


def setup_argparse() -> argparse.ArgumentParser:
    """ configure and return our argparser """
    args = argparse.ArgumentParser(prog='rx-weather', allow_abbrev=True)
    args.add_argument('--just-temp',
                      help='return location and temperature only',
                      const='temp_only',
                      action='store_const')
    args.add_argument('appid',
                      help='open weather map app id key')
    args.add_argument('zip', help='zip code for which to get the weather')
    args.add_argument('--version', action='version',
                      version='%(prog)s '+__version__)

    return args


def main():
    """ application entry point """
    arg_parser = setup_argparse()
    args = arg_parser.parse_args()
    cc = CurrentConditions(args.appid)
    cc.show_for(zip=args.zip, temp_only=args.just_temp)


if __name__ == '__main__':
    main()
