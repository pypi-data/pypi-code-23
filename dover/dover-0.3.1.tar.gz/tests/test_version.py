import pytest
from dover.version import Version, PreRelease, VersionError


def test_prerelease_init():
    pre = PreRelease()
    assert not pre.exists 
    pre.initialize('alpha', 0)
    assert pre.exists


def test_prerelease_str():
    pre = PreRelease()
    assert str(pre) == ''
    pre.initialize('alpha', 0)
    assert str(pre) == '-alpha'
    pre.increment_number()
    assert str(pre) == '-alpha.1'


def test_prerelease_increment():
    variations = [
        ((None, 0), 'alpha', '-alpha'),
        (('alpha', 0), 'alpha', '-alpha.1'),
        (('alpha', 1), 'alpha', '-alpha.2'),
        (('alpha', 0), 'beta', '-beta'),
        (('beta', 0), 'beta', '-beta.1'),
        (('beta', 1), 'beta', '-beta.2'),
        (('beta', 1), 'rc', '-rc'),
        (('rc', 0), 'rc', '-rc.1'),
        (('rc', 1), 'rc', '-rc.2'),
        (('rc', 2), None, '')
    ]
    pre = PreRelease()
    for initialize, increment, expected_results in variations:
        pre.initialize(*initialize)
        pre.increment(increment)
        assert str(pre) == expected_results


def test_prerelease_increment_errors():
    pre = PreRelease()

    pre.initialize('rc', 0)

    with pytest.raises(VersionError):
        pre.increment('alpha')

    with pytest.raises(VersionError):
        pre.increment('beta')

    pre.initialize('beta', 0)

    with pytest.raises(VersionError):
        pre.increment('alpha')

    with pytest.raises(VersionError):
        pre.increment('dev')


def test_init():
    version = Version('0.0.1')
    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 1


def test_version_init_errors():
    with pytest.raises(VersionError):
        version = Version('v0.1.2alpha')


def test_version_copy():
    ver1 = Version('2.3.6-rc.1')
    ver2 = ver1.copy()
    assert ver1 == ver2


def init_variation(initializer, expected):
    version = Version(initializer)
    assert str(version) == expected


def test_init_variations():
    variations = [
        ('0', '0.0.0'),
        ('0.0', '0.0.0'),
        ('0.0.0', '0.0.0'),
        ('2', '2.0.0'),
        ('2.0', '2.0.0'),
        ('2.0.0', '2.0.0'),
        ('0.1', '0.1.0'),
        ('0.1.0', '0.1.0'),
        ('0.1.1', '0.1.1'),
        ('0.1.1-alpha', '0.1.1-alpha')
    ]

    for initializer, expected in variations:
        init_variation(initializer, expected)


def test_formating():
    version = Version('1.1.1')
    assert '{}'.format(version) == '1.1.1'
    assert '{:M}'.format(version) == '1'
    assert '{:Mm}'.format(version) == '1.1'
    assert '{:Mmp}'.format(version) == '1.1.1'


def test_str():
    version = Version('0.0.1')
    assert str(version) == '0.0.1'


def test_to_string():
    version = Version('0.0.1')
    assert str(version) == '0.0.1'


def test_to_tuple():
    version = Version('0.0.1')
    assert version.to_tuple() == (0, 0, 1)


def test_repr():
    version = Version('0.0.1')
    assert repr(version) == '<Version 0.0.1>'


def test_increment_major():
    version = Version('1.1.1')
    version.increment_major()
    assert str(version) == '2.0.0'


def test_increment_minor():
    version = Version('1.1.1')
    version.increment_minor()
    assert str(version) == '1.2.0'


def test_increment_patch():
    version = Version('1.1.1')
    version.increment_patch()
    assert str(version) == '1.1.2'


def test_increment():
    version = Version('0.1.0')

    version.increment('patch')
    assert str(version) == '0.1.1'

    version.increment('patch', 'alpha')
    assert str(version) == '0.1.2-alpha'

    version.increment('patch', 'alpha')
    assert str(version) == '0.1.3-alpha'

    version.increment('minor')
    assert str(version) == '0.2.0'

    version.increment(None, 'beta')
    assert str(version) == '0.2.0-beta'

    version.increment(None, 'beta')
    assert str(version) == '0.2.0-beta.1'

    version.increment(None, 'beta')
    assert str(version) == '0.2.0-beta.2'

    version.increment(None, 'rc')
    assert str(version) == '0.2.0-rc'

    version.increment(None, 'rc')
    assert str(version) == '0.2.0-rc.1'

    version.increment('major')
    assert str(version) == '1.0.0'


def test_increment_errors():
    version = Version('0.1.0')
    with pytest.raises(VersionError):
        version.increment('alpha')

    with pytest.raises(VersionError):
        version.increment(None)

