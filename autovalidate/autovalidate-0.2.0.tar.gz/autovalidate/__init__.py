import fnmatch
import os
import re

from autovalidate.reporters import get_reporter
from autovalidate.validators import get_validator


def find_and_validate(directory, **options):
    exclude_patterns = [re.compile(fnmatch.translate(exclude))
                        for exclude in options.get('exclude', '').split(',')
                        if len(exclude) > 0]

    for root, dirs, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            if any(xp.search(full_path) for xp in exclude_patterns):
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
