import os


def test_import():
    import pyconrad


def test_installation():
    import pyconrad

    assert os.path.exists(pyconrad._download_conrad.conrad_jar_dir())
    assert os.path.exists(pyconrad._download_conrad.conrad_jar_file())


def test_java():
    import pyconrad.autoinit

    pyconrad._pyconrad.PyConrad()._check_jre_version()


if __name__ == "__main__":
    test_import()
    test_installation()
    test_java()
