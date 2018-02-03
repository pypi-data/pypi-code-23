import fnmatch
import os
import re

from autovalidate.reporters import get_reporter
from autovalidate.validators import get_validator


def find_and_validate(directory, **options):
    excludes = [x for x in options.get('exclude', '').split(',')
                if len(x) > 0]

    slash_star = '%s*' % os.sep
    dir_exclude_patterns = [re.compile(fnmatch.translate(x.rstrip(slash_star)))
                            for x in excludes
                            if x.endswith(slash_star)]
    file_exclude_patterns = [re.compile(fnmatch.translate(x))
                             for x in excludes
                             if not x.endswith(slash_star)]

    for dirpath, dirnames, filenames in os.walk(directory):
        # Prune tree while walking to avoid traversing an entire directory tree
        # that has been excluded by a pattern ending in /*
        for dirname in reversed(dirnames):
            full_path = os.path.join(dirpath, dirname)
            if any(xp.search(full_path) for xp in dir_exclude_patterns):
                dirnames.remove(dirname)

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if any(xp.search(full_path) for xp in file_exclude_patterns):
                continue
            basename, ext = os.path.splitext(filename)
            validator = get_validator(ext)
            if validator is None:
                continue
            yield validator.validate(full_path)


def autovalidate(directory, reporter, **options):
    reporter = get_reporter(reporter)
    for result in find_and_validate(directory, **options):
        reporter.record(result)

    reporter.summarize()

    return reporter.invalid_count == 0
