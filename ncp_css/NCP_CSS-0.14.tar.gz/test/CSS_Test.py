import unittest
from NCP_CSS.CSS import CSS


class CSS_Test(unittest.TestCase):

    def setUp(self):
        self.css = CSS(client_id="client_id", client_secret="client_secret")
        pass

    def test_valication_check_when_text_is_null(self):
        with self.assertRaises(ValueError):
            self.css.translate_text(text=None)

    def test_valication_check_when_speaker_error(self):
        with self.assertRaises(ValueError):
            self.css.translate_text(text="안녕하세요", speaker="sjdbfksjdbfkjsdb")

    def test_valication_check_speed_range(self):
        with self.assertRaises(ValueError):
            self.css.translate_text(text="show", speed=-10)
        with self.assertRaises(ValueError):
            self.css.translate_text(text="show", speed=10)


if __name__ == '__main__':
    unittest.main()
