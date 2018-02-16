from os.path import join, dirname
from atelier.test import TestCase
from etgen.sepa.validate import validate_pain001

class SepaTests(TestCase):
    def test_sepa(self):
        fn = join(dirname(__file__), 'finan.PaymentOrder-63.xml')
        validate_pain001(fn)
