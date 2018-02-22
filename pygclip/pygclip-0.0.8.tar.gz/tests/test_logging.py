from pygclip.logging import setup_logging


def test_setup_logging():
    """Test whether the logging level can be set to a default."""
    setup_logging()


def test_setup_logging_debug_mode():
    """Test whether the logging level can be set in debug mode."""
    setup_logging(True)

