import os
import sys

import pytest

from spaceminator.main import create_parser
from spaceminator.main import main


@pytest.mark.parametrize('options, expected', [
    ('', [os.getcwd(), False, False, '_', False, False, False, False]),
    ('-p /home/user/some_dir', ['/home/user/some_dir', False, False, '_', False, False, False, False]),
    ('-l', [os.getcwd(), True, False, '_', False, False, False, False]),
    ('-q', [os.getcwd(), False, True, '_', False, False, False, False]),
    ('-c x', [os.getcwd(), False, False, 'x', False, False, False, False]),
    ('-r', [os.getcwd(), False, False, '_', True, False, False, False]),
    ('-d', [os.getcwd(), False, False, '_', False, True, False, False]),
    ('-f', [os.getcwd(), False, False, '_', False, False, True, False]),
    ('-ln', [os.getcwd(), False, False, '_', False, False, False, True]),

])
def test_create_parser(options, expected):
    parser = create_parser()
    argv = options.split()
    args = parser.parse_args(argv)
    assert args.path == expected[0]
    assert args.list == expected[1]
    assert args.quiet == expected[2]
    assert args.char == expected[3]
    assert args.recursive == expected[4]
    assert args.dirs_only == expected[5]
    assert args.files_only == expected[6]
    assert args.links_only == expected[7]


@pytest.mark.parametrize('options', [
    '-d -f', '-f -ln', '-d -ln', '-d -f -ln'
])
def test_create_parser_raises(options):
    parser = create_parser()
    argv = options.split()
    with pytest.raises(SystemExit):
        parser.parse_args(argv)


@pytest.mark.parametrize('option, file_type', [
    ('-d', 'Dir',),
    ('-f', 'File',),
    ('-ln', 'Symlink',),
    ('', None),
])
def test_main(mocker, option, file_type):
    mocked_Spaceminator = mocker.patch('spaceminator.main.Spaceminator')
    sys.argv[1:] = option.split()

    main()

    mocked_Spaceminator.assert_called_with(
        path=os.getcwd(), list_only=False, quiet=False, char='_', recursive=False, file_type=file_type)

    assert mocked_Spaceminator.return_value.spaceminate.called
