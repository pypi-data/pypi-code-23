# -*- coding: utf-8 -*-


def test_validate_litezip(datadir):
    args = [str(datadir / 'litezip')]

    from litezip.cli.validate import main
    retcode = main(args)

    assert retcode == 0


def test_validate_invalid_litezip(datadir, capsys):
    args = [str(datadir / 'invalid_litezip')]

    from litezip.cli.validate import main
    retcode = main(args)

    assert retcode == 1

    out, err = capsys.readouterr()
    assert not out


def test_validate_litezip_verbose_output(datadir, capsys):
    args = ['-v', str(datadir / 'invalid_litezip')]

    from litezip.cli.validate import main
    retcode = main(args)

    assert retcode == 1

    out, err = capsys.readouterr()
    assert 'collection.xml: 114:13 -- error: element' in out
    assert 'mux is not a valid identifier' in out
    assert 'mux/index.cnxml: 61:10 -- error: unknown element "foo"' in out


def test_validate_litezip_quiet_output(datadir, capsys):
    args = ['-q', str(datadir / 'invalid_litezip')]

    from litezip.cli.validate import main
    retcode = main(args)

    assert retcode == 1

    out, err = capsys.readouterr()
    assert not out
