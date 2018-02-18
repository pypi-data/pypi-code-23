def _test_install():
    try:
        from . import conftest  # noqa
    except ImportError:
        pass
    else:
        raise EnvironmentError()
