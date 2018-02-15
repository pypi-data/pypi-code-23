import unittest
import rechistoso
from rechistoso.cli import main


class TestChiste(unittest.TestCase):

    """Testeando el chiste que está re bueno"""

    def setUp(self):
        self.chiste = rechistoso.chiste()

    def test_chiste_devuelve_cadena(self):
        self.assertIsInstance(self.chiste, str)

    def test_chiste_correcto(self):
        CHISTE = """
        ¿Qué le dice un árbol a otro árbol? – Nos han dejado plantados.
        """
        self.assertEqual(self.chiste.strip().lower(), CHISTE.strip().lower())

    def test_cli(self):
        self.assertEqual(self.chiste, main())
