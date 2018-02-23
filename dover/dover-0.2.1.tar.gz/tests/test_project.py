import pytest
from pathlib import Path
from difflib import ndiff
from dover import project


def test_find_config_file():
    cfg_file = project.find_config_file()
    assert cfg_file is not None
    assert cfg_file.name == 'setup.cfg'


def test_find_config_file_failure(tmpdir):
    with pytest.raises(project.ConfigurationError) as ex_info:
        project.find_config_file(tmpdir)

    err_msg = 'Dover found no configuration files!'
    assert ex_info.value.args[0] == err_msg


def test_collect_versioned_files():
    # this is using dover package as the test source
    cfg_file = project.find_config_file()
    versioned_files = project.collect_versioned_files(cfg_file)

    assert len(versioned_files) == 4
    assert versioned_files[0].name == 'setup.py'
    assert versioned_files[1].name == 'setup.cfg'
    assert versioned_files[2].name == 'cli.py'
    assert versioned_files[3].name == 'README.md'


def test_collect_versioned_files_failure(tmpdir):
    cfg_file = Path(tmpdir, 'setup.cfg')
    with cfg_file.open('w') as fh_:
        fh_.write('\n\n[dover:file:somepath.py]\n')

    with pytest.raises(project.ConfigurationError) as ex_info:
        project.collect_versioned_files(cfg_file)

    err_msg = 'Invalid configuration section: [dover:file:somepath.py]. Path does not exist.'
    assert ex_info.value.args[0] == err_msg


variations = [
    ('0.2', 'v0.2'),
    ('0.2', 'version = 0.2'),
    ('0.2', '__version__ = 0.2'),
    ('0.2', '    version = 0.2    \n'),
    ('0.2', '    __version__ = 0.2   \n'),
    ('0.2', "version = '0.2'"),
    ('0.2', 'version = "0.2"'),
    ('0.2', 'version 0.2'),
    ('0.2', "__version__ = '0.2'"),
    ('0.2', '__version__ = "0.2"'),
    ('0.3.0', 'version = 0.3.0'),
    ('0.3.0', 'version = 0.3.0 \n'),
    ('0.3.0', 'version 0.3.0 \n'),

    ('0.2.4', '![version-badge](https://img.shields.io/badge/version-v0.2.4-green.svg "v0.2.4")')
]


@pytest.fixture(params=variations)
def test_version_regex(request):
    expected, version_match = request.param
    rx = project.version_regex()
    m = rx(version_match)
    assert m is not None
    assert m.groupdict()['version'] == expected


FILE_SAMPLE = ["import os", "__version__ = '0.1.0'", "", "value = 1"]


@pytest.fixture
def sample():
    vfile = project.VersionedFile()
    vfile.content = FILE_SAMPLE
    vfile.collect_version_info()
    yield vfile


def test_versionfile_collect_version_info(sample):
    assert len(sample.versioned_lines) == 1


def test_assert_versions(files):

    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)
    print(vfiles[0].versioned_lines)
    asserted_files = project.assert_versions(vfiles)

    assert asserted_files == '0.3.0'


def test_assert_versions_failure(files):

    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)

    # insert additional bogus version number
    vfiles[0].versioned_lines.append((99, "version = '2.6.1'", '2.6.1'))

    print(vfiles[0].versioned_lines)

    with pytest.raises(project.VersionMissMatchError) as ex_info:
        project.assert_versions(vfiles)

    assert ex_info.value.args[0] == ('Not all file versions match:\n\n'
                                     "    setup.py    0.3.0 (__version__ = '0.3.0') \n"
                                     "    setup.py    2.6.1 (version = '2.6.1')     \n"
                                     "    setup.cfg   0.3.0 (version = 0.3.0)       \n"
                                     "    newd/cli.py 0.3.0 (__version__ = '0.3.0') \n"
                                     "    README.md   0.3.0 (#### newd app v0.3.0)  ")


def test_print_versioned_lines(files, capsys):
    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)

    project.print_versioned_lines(vfiles)

    captured = capsys.readouterr()

    assert captured.out == ("    setup.py    0005 (__version__ = '0.3.0') \n"
                            "    setup.cfg   0002 (version = 0.3.0)       \n"
                            "    newd/cli.py 0002 (__version__ = '0.3.0') \n"
                            "    README.md   0000 (#### newd app v0.3.0)  \n")


def test_print_versioned_updates(files, capsys):

    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)

    project.print_versioned_updates(vfiles, '0.4.0')

    captured = capsys.readouterr()

    assert captured.out == ("    setup.py    (0.3.0 -> 0.4.0)\n"
                            "    setup.cfg   (0.3.0 -> 0.4.0)\n"
                            "    newd/cli.py (0.3.0 -> 0.4.0)\n"
                            "    README.md   (0.3.0 -> 0.4.0)\n")


def test_versionedfile_update(files):

    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)

    vfiles[0].update('0.4.0')
    assert vfiles[0].content[5] == "__version__ = '0.4.0'\n"

    vfiles[1].update('0.4.0')
    assert vfiles[1].content[2] == 'version = 0.4.0\n'

    vfiles[2].update('0.4.0')
    assert vfiles[2].content[2] == "__version__ = '0.4.0'\n"

    vfiles[3].update('0.4.0')
    assert vfiles[3].content[0] == '#### newd app v0.4.0\n'


def do_diff(a, b):
    diff = ndiff(a, b)
    lines = [line for line in diff if line[0] in ('+', '-')]
    return ''.join(lines)


def compare_save_diff(vfile, src_content, diff_string):

    print('comparing {}'.format(vfile.name))

    vfile.update('0.4.0')
    vfile.save()

    with vfile.file_path.open('r') as fh_:
        org_content = src_content.splitlines(keepends=True)
        new_content = fh_.read().splitlines(keepends=True)
        diff = do_diff(org_content, new_content)
        assert diff == diff_string


def test_versionedfile_save(files):

    config = project.find_config_file(cwd=files.temp_dir)
    vfiles = project.collect_versioned_files(config)

    compare_save_diff(vfiles[0],
                      files.setup_py_content,
                      "- __version__ = '0.3.0'\n+ __version__ = '0.4.0'\n")

    compare_save_diff(vfiles[1],
                      files.setup_cfg_content,
                      "- version = 0.3.0\n+ version = 0.4.0\n")

    compare_save_diff(vfiles[2],
                      files.cli_py_content,
                      "- __version__ = '0.3.0'\n+ __version__ = '0.4.0'\n")

    compare_save_diff(vfiles[3],
                      files.readme_content,
                      "- #### newd app v0.3.0\n+ #### newd app v0.4.0\n")
