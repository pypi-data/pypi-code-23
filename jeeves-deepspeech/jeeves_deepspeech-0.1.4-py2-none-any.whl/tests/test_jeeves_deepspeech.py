import sys
import unittest

from jeeves_deepspeech import DeepSpeechSTT


class TestJeevesDeepSpeech(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        stt = DeepSpeechSTT()
        self.assertFalse(stt is None)


if __name__ == '__main__':
    unittest.main()
