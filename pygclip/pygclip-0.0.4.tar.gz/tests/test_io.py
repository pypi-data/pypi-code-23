from pygclip.io import run_shell_command, write_html_to_clipboard


def test_run_shell_command():
    """Test that a simple shell command returns the expected output."""
    assert run_shell_command(['echo', 'hello world']) == "hello world\n"


def test_write_html_to_clipboard(clipboard):
    """Test whether HTML is correctly encoded into the OSX clipboard."""
    write_html_to_clipboard('<p></p>')
    assert clipboard() == '<p></p>'
    assert clipboard(raw=True) == u"\xabdata HTML3C703E3C2F703E\xbb\n"
