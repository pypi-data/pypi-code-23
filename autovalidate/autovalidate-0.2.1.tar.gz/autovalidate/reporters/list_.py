from autovalidate.reporters.core import Reporter, reporter


@reporter('list')
class ListReporter(Reporter):
    def report(self, result):
        if result.valid:
            self.write(u'\033[92m\u2713\033[0m %s\n' % result.path)
        else:
            self.write(u'\033[91m\u2717 %s\033[0m\n' % result.path)
