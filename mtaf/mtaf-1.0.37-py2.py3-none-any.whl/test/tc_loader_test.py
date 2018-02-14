import argparse
import unittest

parser = argparse.ArgumentParser()
parser.add_argument("site_tag", choices=['mm', 'js', 'local'], help="site tag, selects config/site_<tag>.json file")
parser.add_argument('-c', '--cfg_host', help='name of mongodb server for test configuration, default "vqda"',
                    default='vqda')
args = parser.parse_args()

from ePhone7.config.configure import cfg

cfg.set_site(args.cfg_host, args.site_tag)

# suite = unittest.TestSuite()
# suite.addTest(unittest.TestLoader().loadTestsFromTestCase(smoke.SmokeTests))
import ePhone7.suites.smoke as smoke
suite = unittest.TestSuite()
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(smoke.SmokeTests))
names = unittest.TestLoader().getTestCaseNames(suite)
for name in names:
    print name
