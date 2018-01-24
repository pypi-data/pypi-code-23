import nfqueue

from iceman.configuration import Configuration
from iceman.traffic.traffic import Traffic

def configuration():
    config = Configuration()
    config.cipher_suite = config.initialize_cipher_suite('fernet')
    return config


class TestInstance(object):
    def test_instance(self):
        egress_queue = 0
        ingress_queue = 1
        config = configuration()

        subject = Traffic(egress_queue,
                          ingress_queue,
                          config.cipher_suite,
                          config.encryption_enabled)
        assert subject.__class__.__name__ == 'Traffic'
        assert subject.egress_queue == egress_queue
        assert subject.ingress_queue == ingress_queue

class TestTransform(object):
    def test_transform(self, mocker):

        # mocker.patch('nfqueue.queue.set_verdict_modified')

        egress_queue = 0
        ingress_queue = 1
        config = configuration()

        subject = Traffic(egress_queue,
                          ingress_queue,
                          config.cipher_suite,
                          config.encryption_enabled)
        # mocker.patch('nfqueue.set_verdict_modified')
        # obj.ingress()
        # assert Interceptor.intercept.call_count == 1

