from contextlib import contextmanager
import fpdf


class Pdf(fpdf.FPDF):

    @contextmanager
    def clipping_rect(self, x, y, width, height):
        self._out('q %.2F %.2F %.2F %.2F re W n' %
                 (x*self.k, (self.h-y)*self.k, width*self.k, -height*self.k))
        yield
        self._out('Q')
