import os
import sys
import tempfile

import pytest
import filecmp
import difflib

from mklist.generate_parts_lst import generate_parts_lst


@pytest.mark.parametrize('mode',['description'])
def test_generate_test_data(mode):
    _, parts_file = tempfile.mkstemp(suffix='.lst')
    generate_parts_lst(mode,
                       parts_folder_path=os.path.join('tests', 'test_data', 'test_parts'),
                       parts_lst_path=parts_file
                       )
    expected_parts_file = os.path.join('tests', 'test_data', 'parts.%s.lst' % mode)

    comparison = filecmp.cmp(parts_file, expected_parts_file, shallow=False)

    if not comparison:
        content = open(parts_file).readlines()
        expected = open(expected_parts_file).readlines()
        for line in difflib.context_diff(expected, content, fromfile='expected', tofile='content'):
            sys.stdout.write(line)

    assert comparison
