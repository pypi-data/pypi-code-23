from os import path
from unittest.mock import patch
import subprocess


def _run_cli(*args):
    """Run the jinjafy cli command from the tests/ directory, passing in the provided arguments"""
    return subprocess.run(
        ['jinjafy', *args],
        # Execute in the same directory as this test file
        cwd=path.dirname(__file__),
        # stdout as text
        encoding='utf-8',
        # capture stderr stdout in the completed process
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

def test_cli():
    """The jinjafy command works for a simple case"""
    ps = _run_cli('shakespeare.j2', 'love=laughter')
    
    expected = """Let me not to the marriage of true minds
Admit impediments. laughter is not laughter
Which alters when it alteration finds,
Or bends with the remover to remove
"""

    assert ps.stdout == expected

def test_cli_args_missing():
    """Missing variables should write to stderr"""
    ps = _run_cli('shakespeare.j2')

    assert ps.returncode != 0
    assert 'love' in ps.stderr

def test_verbose_doesnt_break_stdout():
    """Verbose shouldn't pollute stdout"""
    ps = _run_cli('--verbose', 'shakespeare.j2', 'love=friendship')

    expected = """Let me not to the marriage of true minds
Admit impediments. friendship is not friendship
Which alters when it alteration finds,
Or bends with the remover to remove
"""
    assert ps.stderr != ''
    assert ps.stdout == expected
