import sys

class Progress(object):
    def __init__(self, step_size=0.1, method='bar'):
        self.step_size = step_size
        self.method = method

    def log(self, progress):
        if self.method == 'bar':
            print "\r" + self._get_bar(progress),
            sys.stdout.flush()

    def _get_bar(self, progress):
        if progress <= 1.:
            progress_str_done = ["#"]*int(progress/self.step_size)
            progess_str_not_done = [" "] * int((1. - progress) / self.step_size)
            progress_str = "[" + ''.join(progress_str_done + progess_str_not_done) + "]"

            return progress_str