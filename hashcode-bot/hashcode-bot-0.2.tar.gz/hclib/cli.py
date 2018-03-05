import time

import halo
import click


def download_progress(request, path):
    with path.open('wb') as fh:
        for chunk in request.iter_content(chunk_size=1024):
            if chunk:
                fh.write(chunk)


class FailExecution(Exception):
    pass


class SkipExecution(Exception):
    pass


class SkippableSpinner(halo.Halo):
    def skip(self, note='skipped'):
        note = click.style(f'({note})', fg='cyan')
        self.info(f'{self.text} {note}')
        raise SkipExecution

    def fail(self, *args, **kwargs):
        super().fail(*args, **kwargs)
        raise FailExecution

    def __exit__(self, type, value, traceback):
        if not type:
            self.succeed()
        elif type in [SkipExecution, FailExecution]:
            return True
        else:
            self.fail()


spinner = SkippableSpinner


class TimedSpinner(SkippableSpinner):
    def __enter__(self):
        self._start_time = time.perf_counter()
        return super().__enter__()

    def __exit__(self, type, value, traceback):
        duration = time.perf_counter() - self._start_time
        timing = click.style(f'({duration:.1f}s)', fg='cyan')
        self.text = f'{self.text} {timing}'
        return super().__exit__(type, value, traceback)


timed_spinner = TimedSpinner
