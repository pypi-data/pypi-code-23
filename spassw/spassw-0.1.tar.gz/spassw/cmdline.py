import sys
import argparse
import logging



def get_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger



from .spassw import generate_password

def spassw_run(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=u'Simple Password Generator')
    parser.add_argument(u'--length', help=u'Password length')
    parser.add_argument(u'--letters', dest='letters', action='store_true')
    parser.add_argument(u'--no-letters', dest='letters', action='store_false')
    parser.add_argument(u'--digits', dest='digits', action='store_true')
    parser.add_argument(u'--no-digits', dest='digits', action='store_false')
    parser.add_argument(u'--punctuation', dest='punctuation', action='store_true')
    parser.add_argument(u'--no-punctuation', dest='punctuation', action='store_false')
    parser.set_defaults(letters=True)
    parser.set_defaults(digits=True)
    parser.set_defaults(punctuation=False)
    
    opts = parser.parse_args(argv)
    password = generate_password(opts)
    get_logger().debug('Generated spassw:  %s', password)