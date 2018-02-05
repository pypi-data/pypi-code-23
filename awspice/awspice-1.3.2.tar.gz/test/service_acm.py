import unittest
import random
from awsmanager import AwsManager, ClsEncoder

class ServiceAcmTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\nStarting unit tests of Service.ACM")

    #################################
    # -------- INSTANCES ---------- #
    #################################

    def test_get_certificate(self):
        aws = AwsManager('eu-west-1', profile='4p')
        arn = 'arn:aws:acm:eu-west-1:556856487218:certificate/1abada27-8665-45e9-8034-1e869234a77a'
        certificate = aws.service.acm.get_certificate(arn, regions=['eu-west-1'])
        self.assertEquals(certificate['DomainName'], 'api.int.baikalplatform.com')

    def test_get_certificate_by(self):
        aws = AwsManager('eu-west-1', profile='4p')
        certificate = aws.service.acm.get_certificate_by('domain', 'api.int.baikalplatform.com', regions=['eu-west-1'])
        self.assertEquals(certificate['Issuer'], 'Telefonica')


if __name__ == '__main__':
        unittest.main()
