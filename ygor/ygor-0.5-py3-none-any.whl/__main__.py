import argparse
from pathlib import Path
from collections import defaultdict
import importlib
import importlib.util
from signal import signal, SIGPIPE, SIG_DFL

from ygor import Context, Job


class Query:
    def __init__(self, s):
        self.key, self.value = s.split('=')
        for func in (int, float):
            try:
                self.value = func(self.value)
            except ValueError:
                continue


def get_param_widths(jobs):
    maxwidths = defaultdict(int)
    for job in jobs:
        for key in job._params:
            value = getattr(job, key)
            maxwidths[key] = max(maxwidths[key], len(str(value)), len(key))
    return maxwidths


def import_job_class(job_specifier):
    path, class_name = job_specifier.split(':')
    path = Path(path)
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)


def get_jobs(args, query={}):
    context = Context(args.directory)

    # Query
    if args.job_class:
        job_cls = import_job_class(args.job_class)
        jobs = context.query_jobs_with_class(job_cls, **query)
    else:
        jobs = context.query_jobs(**query)

    # Filter on status
    for job in jobs:
        job.context = context
        try:
            status = args.status
        except AttributeError:
            status = None

        if status is None or job.is_done() == status:
            yield job



def print_header(maxwidths, with_done=False):
    if with_done:
        header = '    ' + ' '.join([f'{key:<{maxwidths[key]}s}' for key, value in maxwidths.items()]) + ' hash'
    else:
        header = ' '.join([f'{key:<{maxwidths[key]}s}' for key, value in maxwidths.items()]) + ' hash'
    print(header)


def print_job(job, maxwidths=None):
    params = {key: getattr(job, key) for key in job._params}
    if maxwidths:
        params_str = ' '.join(f'{value:<{maxwidths[key]}s}' for key, value in params.items())
    else:
        params_str = ' '.join(f'{key}={value}' for key, value in params.items())

    if type(job) is Job:
        print(f'{params_str} {job.hash}')
    else:
        completed = '[X]' if job.is_done() else '[ ]'
        print(f'{completed:3s} {params_str} {job.hash}')


def print_job_list(args, jobs):
    maxwidths = get_param_widths(jobs)

    print_header(maxwidths, with_done=args.job_class)

    for job in jobs:
        print_job(job, maxwidths)



def main_ls(args):
    jobs = list(get_jobs(args))
    print_job_list(args, jobs)


def main_find(args):
    query_dict = {q.key: q.value for q in args.query}
    jobs = list(get_jobs(args, query_dict))
    print_job_list(args, jobs)


def main():
    # Catch SIGPIPE to allow piping to less without going haywire
    signal(SIGPIPE, SIG_DFL)

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_ls = subparsers.add_parser('ls', help='List experiments in directory')
    parser_ls.set_defaults(func=main_ls)

    parser_find = subparsers.add_parser('find', help='Find jobs matching search')
    parser_find.add_argument('query', nargs='+', type=Query)
    status_group = parser_find.add_mutually_exclusive_group()
    status_group.add_argument('--done', action='store_true', dest='status', default=None)
    status_group.add_argument('--not-done', action='store_false', dest='status', default=None)
    parser_find.set_defaults(func=main_find)

    for subp in (parser_ls, parser_find):
        subp.add_argument('-d', '--directory', type=Path, default=Path('.'), required=False)
        subp.add_argument('-j', '--job-class', help='Job class as foo.py:FooJob', required=False)

    # Run the correct subparser
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()