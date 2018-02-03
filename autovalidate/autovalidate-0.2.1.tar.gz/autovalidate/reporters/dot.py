from autovalidate.reporters.core import Reporter, reporter


@reporter('dot')
class DotReporter(Reporter):
    def report(self, result):
        self.write('.' if result.valid else 'F')

    def summarize(self):
        self.write('\n')
        super(DotReporter, self).summarize()
