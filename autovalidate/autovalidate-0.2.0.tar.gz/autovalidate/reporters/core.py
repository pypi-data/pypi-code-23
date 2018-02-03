import sys

from autovalidate.utils import indent


class Reporter(object):
    def __init__(self, out):
        self.out = out
        self.valid_results = []
        self.invalid_results = []

    @property
    def valid_count(self):
        return len(self.valid_results)

    @property
    def invalid_count(self):
        return len(self.invalid_results)

    def record(self, result):
        if result.valid:
            self.valid_results.append(result)
        else:
            self.invalid_results.append(result)

        self.report(result)

    def report(self, result):
        raise NotImplementedError

    def summarize(self):
        for result in self.invalid_results:
            self.out.write('\n%s:\n%s\n' % (result.path,
                                            indent(result.message)))
        self.out.write('\n%d valid, %d invalid\n' % (self.valid_count,
                                                     self.invalid_count))

reporter_classes = {}


def reporter(format):
    def reporter_decorator(cls):
        reporter_classes[format] = cls
        return cls
    return reporter_decorator


def get_reporter(name, out=None):
    if name not in reporter_classes:
        raise ValueError('unknown reporter: "%s"' % name)
    if out is None:
        out = sys.stdout
    return reporter_classes[name](out)
