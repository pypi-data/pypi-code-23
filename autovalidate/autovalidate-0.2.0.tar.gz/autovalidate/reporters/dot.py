from autovalidate.reporters.core import Reporter, reporter


@reporter('dot')
class DotReporter(Reporter):
    def report(self, result):
        self.out.write('.' if result.valid else 'F')

    def summarize(self):
        self.out.write('\n')
        super(DotReporter, self).summarize()
