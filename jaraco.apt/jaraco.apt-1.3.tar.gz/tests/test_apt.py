from jaraco import apt

sample_output = """
Stuff
  More stuff
The following NEW packages will be installed:
  abc{a} def{a} ghi jk lmno pqwerty{a}
  xyz
  g++
Even more stuff
Stuff again
"""

def test_parse_new_packages():
    pkgs = apt.parse_new_packages(sample_output)
    assert not any('stuff' in pkg.lower() for pkg in pkgs)
    assert 'abc' not in pkgs
    assert pkgs == ['ghi', 'jk', 'lmno', 'xyz', 'g++']

def test_parse_new_packages_include_automatic():
    pkgs = apt.parse_new_packages(sample_output, include_automatic=True)
    assert not any('stuff' in pkg.lower() for pkg in pkgs)
    assert pkgs == ['abc', 'def', 'ghi', 'jk', 'lmno', 'pqwerty', 'xyz',
        'g++']
