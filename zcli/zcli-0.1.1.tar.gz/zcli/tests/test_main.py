from unittest import TestCase
from mock import MagicMock, call, patch, sentinel
from zcli.main import main


class main_tests (TestCase):
    @patch('sys.stdout')
    @patch('zcli.clargs.parse_args')
    @patch('zcli.zcashcli.ZcashCLI')
    def test_main(self, m_ZcashCLI, m_parse_args, m_stdout):
        m_run = MagicMock()
        m_run.return_value = ["json", "result"]

        m_parse_args.return_value = (
            {'DEBUG': True, 'DATADIR': sentinel.DATADIR},
            m_run,
            {'fake_arg': sentinel.FAKE_ARG},
        )

        main(sentinel.ARGS)

        self.assertEqual(
            m_parse_args.mock_calls,
            [call(main.__doc__, sentinel.ARGS),
             ])
        # call().cmdclass.run(m_ZcashCLI.return_value)])

        self.assertEqual(
            m_ZcashCLI.mock_calls,
            [call(sentinel.DATADIR)])

        self.assertEqual(
            m_stdout.mock_calls,
            [call.write('[\n  "json",\n  "result"\n]')])
