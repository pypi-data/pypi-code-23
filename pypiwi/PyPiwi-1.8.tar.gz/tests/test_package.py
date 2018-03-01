# -*- coding: utf-8 -*-
from os import path

import check_manifest
import pip
import pytest
from pip.download import PipSession
from pip.index import PackageFinder
from pip.locations import USER_CACHE_DIR
from pip.models import PyPI

slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


def test_is_present():
    import pypiwi
    assert pypiwi


@slow
def test_manifest():
    dirname = path.dirname(__file__) + '/../'
    assert check_manifest.check_manifest(dirname) is True


@slow
def test_pip():
    finder = PackageFinder([], [PyPI.simple_url],
                           session=PipSession(cache=(USER_CACHE_DIR)))

    def find_latest_candidate(package_name):
        all_candidates = finder.find_all_candidates(package_name)
        # Remove prereleases
        all_candidates = [candidate for candidate in all_candidates
                          if not candidate.version.is_prerelease]
        return max(all_candidates,
                   key=finder._candidate_sort_key)

    ignore = list()
    packages = list()
    comparison = list()

    for dist in pip.get_installed_distributions():
        if dist.project_name in ignore:
            continue
        online = find_latest_candidate(dist.project_name)
        if dist.parsed_version < online.version:
            packages.append(dist.project_name)
            comparison.append(
                '%20s %10s  < %10s' % (dist.project_name, dist.version,
                                       online.version))

    if len(comparison):
        message = 'The following packages should be updated:\n%s\n' \
                  'Run the following command:\n' \
                  'pip install -U %s && pip freeze > requirements.txt\n' \
                  '\nMake sure you run the tests again!'

        assert False, message % ('\n'.join(comparison), ' '.join(packages))
