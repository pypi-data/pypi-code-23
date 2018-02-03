# -*- coding: utf-8 -*-
"""Unittest module."""
import unittest
import datetime
from buzio.cli import Console
from collections import OrderedDict
from colorama import Fore


class ConsoleClassTest(unittest.TestCase):
    """Unit Tests for Console Class."""

    def setUp(self):
        """Set Up class."""
        super(ConsoleClassTest, self).setUp()
        self.instance = Console()

    def test_terminal_size(self):
        """test_terminal_size."""
        from buzio.cli import get_terminal_size
        ret = get_terminal_size()
        self.assertIsInstance(
            ret, tuple
        )

    def test_get_style(self):
        """test_get_style."""
        self.instance.theme = "warning"
        ret = self.instance._get_style()
        self.assertEqual(
            ret,
            Fore.YELLOW
        )

    def test_get_wrong_style(self):
        """test_get_wrong_style."""
        self.instance.theme = "do-not-exist"
        ret = self.instance._get_style()
        self.assertEqual(
            ret,
            ""
        )

    def test_humanize_none(self):
        """test_humanize_none."""
        obj = None
        ret = self.instance._humanize(obj)
        self.assertEqual(ret, "--")

    def test_humanize_string(self):
        """test_humanize_string."""
        obj = "Hello World!"
        ret = self.instance._humanize(obj)
        self.assertEqual(ret, str(obj))

    def test_humanize_bool(self):
        """test_humanize_bool."""
        obj = True
        ret = self.instance._humanize(obj)
        self.assertEqual(ret, "Yes")

    def test_humanize_datetime(self):
        """test_humanize_bool."""
        obj = datetime.datetime.today()
        ret = self.instance._humanize(obj)
        self.assertEqual(ret, obj.isoformat())

    def test_humanize_datetime_custom_format(self):
        """test_humanize_datetime_custom_format."""
        obj = datetime.datetime.today()
        ret = self.instance._humanize(obj, date_format="%a, %b-%d-%Y")
        self.assertEqual(ret, obj.strftime("%a, %b-%d-%Y"))

    def test_humanize_dictionary(self):
        """test_humanize_dictionary."""
        a = False
        b = datetime.date(2018, 2, 2)
        obj = OrderedDict([("a", a), ("b", b)])
        ret = self.instance._humanize(obj)
        self.assertEqual(
            ret,
            "a: No\nb: 2018-02-02"
        )

    def test_humanize_dictionary_with_counters(self):
        """test_humanize_dictionary_with_counters."""
        a = False
        b = datetime.date(2018, 2, 2)
        obj = OrderedDict([("a", a), ("b", b)])
        ret = self.instance._humanize(obj, show_counters=True)
        self.assertEqual(
            ret,
            "(1) a: No\n(2) b: 2018-02-02"
        )

    def test_print_with_prefix(self):
        """test_print_with_prefix."""
        self.instance.text = "Hello World"
        self.instance.prefix = "Test"
        ret = self.instance._print()
        self.assertEqual(
            ret,
            "Test: Hello World"
        )

    def test_print_with_transform(self):
        """test_print_with_transform."""
        self.instance.text = "Hello World"
        self.instance.transform = "upper"
        ret = self.instance._print()
        self.assertEqual(
            ret,
            "HELLO WORLD"
        )

    def test_print_with_theme(self):
        """test_print_with_theme."""
        self.instance.text = "Hello World"
        self.instance.theme = "success"
        ret = self.instance._print()
        self.assertEqual(
            ret,
            "\x1b[32mHello World\x1b[0m"
        )

    def test_success(self):
        """test_success."""
        ret = self.instance.success("Hello World")
        self.assertEqual(
            ret,
            "\x1b[32mSuccess: Hello World\x1b[0m"
        )

    def test_info(self):
        """test_info."""
        ret = self.instance.info("Hello World")
        self.assertEqual(
            ret,
            "\x1b[36mInfo: Hello World\x1b[0m"
        )

    def test_warning(self):
        """test_warning."""
        ret = self.instance.warning("Hello World")
        self.assertEqual(
            ret,
            "\x1b[33mWarning: Hello World\x1b[0m"
        )

    def test_error(self):
        """test_error."""
        ret = self.instance.error("Hello World")
        self.assertEqual(
            ret,
            "\x1b[31mError: Hello World\x1b[0m"
        )

    def test_section(self):
        """test_section."""
        ret = self.instance.section("Hello World")
        self.assertEqual(
            ret,
            "\x1b[93m\x1b[0m\x1b[93m>> Hello World"
            "\x1b[0m\x1b[93m--------------\x1b[0m\x1b[93m\x1b[0m"
        )

    def test_box_single_line(self):
        """test_box_single_line."""
        ret = self.instance.box("Hello World")
        self.assertEqual(
            ret,
            '\x1b[36m*****************\x1b[0m\x1b[36m*'
            '               *\x1b[0m\x1b[36m*  Hello World'
            '  *\x1b[0m\x1b[36m*               '
            '*\x1b[0m\x1b[36m*****************\x1b[0m'
        )

    def test_box_multi_line(self):
        """test_box_multi_line."""
        ret = self.instance.box("Hello\nWorld")
        self.assertEqual(
            ret,
            '\x1b[36m***********\x1b[0m\x1b[36m*         '
            '*\x1b[0m\x1b[36m*  Hello  *\x1b[0m\x1b[36m*'
            '  World  *\x1b[0m\x1b[36m*         *\x1b[0m\x1b[36m*****'
            '******\x1b[0m'
        )

    def test_unittext(self):
        """test_unittext."""
        ret = self.instance.unitext("São Tomé das Letras")
        self.assertEqual(
            ret,
            "Sao Tome das Letras"
        )

    def test_slugify(self):
        """test_slugify."""
        ret = self.instance.slugify("São Tomé das Letras")
        self.assertEqual(
            ret,
            "sao_tome_das_letras"
        )

    def test_progress(self):
        """test_progress."""
        ret = self.instance.progress(count=5, total=10)
        self.assertEqual(
            ret,
            "\rReading |█████████████████████████------"
            "-------------------| 50.00% Complete "
        )

    def test_load_new_theme(self):
        """test_load_new_theme."""
        new_theme = {
            'test': Fore.RED
        }
        self.instance.load_theme(new_theme)
        self.instance.theme = 'test'
        self.assertEqual(
            self.instance._get_style(),
            Fore.RED
        )

    def test_confirm(self):
        """test_confirm."""
        self.instance.format_only = True
        ret = self.instance.confirm()
        self.assertEqual(
            ret[0],
            '\x1b[95mPlease confirm (y/n) \x1b[0m'
        )

    def test_choose(self):
        """test_choose."""
        self.instance.format_only = True
        options = ["Apple", "Orange", "Banana"]
        ret = self.instance.choose(options)
        self.assertEqual(
            ret[1],
            '\x1b[93m2. Orange\x1b[0m'
        )

    def test_choose_with_default(self):
        """test_choose_with_default."""
        self.instance.format_only = True
        options = ["Apple", "Orange", "Banana"]
        ret = self.instance.choose(options, default="Apple")
        self.assertEqual(
            ret[-1],
            '\x1b[93m\x1b[0m'
        )

    def test_ask(self):
        """test_ask."""
        self.instance.format_only = True
        ret = self.instance.ask('How many tests')
        self.assertEqual(
            ret[0],
            '\x1b[33mHow many tests \x1b[0m'
        )

    def test_select(self):
        """test_select."""
        self.instance.format_only = True
        options = ['orange', 'apples']
        ret = self.instance.select(options)
        self.assertEqual(
            ret[0],
            '\x1b[93mSelect: (O)range, (A)pples\x1b[0m'
        )

    def test_run(self):
        """test_run."""
        command = "echo Hello World"
        ret = self.instance.run(command)
        self.assertTrue(ret)

    def test_get_stdout_from_run(self):
        """test_get_stdout_from_run."""
        command = "echo Hello World"
        ret = self.instance.run(command, get_stdout=True)
        self.assertEqual(
            ret,
            'Hello World\n'
        )
