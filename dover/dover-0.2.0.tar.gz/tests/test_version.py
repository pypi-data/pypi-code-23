import os
import dover
from dover.version import Version
from dover.version import _formating_


def test_init():
    version = Version('0.0.1')
    assert version.major == 0
    assert version.minor == 0
    assert version.patch == 1


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
