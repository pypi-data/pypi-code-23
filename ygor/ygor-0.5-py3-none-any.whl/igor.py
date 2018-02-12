import json
import hashlib
import pathlib
import contextlib

try:
    from tqdm import tqdm
    progressbar = tqdm
except ImportError:
    def progressbar(iterable):
        return iterable


def _test_condition(x, condition_or_value):
    if callable(condition_or_value):
        return condition_or_value(x)
    else:
        return x == condition_or_value


class Context:
    def __init__(self, output_dir, config={}):
        self.output_dir = pathlib.Path(output_dir)
        self._check_and_write_config(config)

    def run_jobs(self, job_list):
        jobs_to_run = []
        for job in job_list:
            self._setup_job(job)
            if not job.is_done():
                jobs_to_run.append(job)

        print(f'{len(jobs_to_run)} of {len(job_list)} needs running')
        for job in progressbar(jobs_to_run):
            with self.job_file(job, 'output.log').open('a') as log_file, \
                 contextlib.redirect_stdout(log_file), \
                 contextlib.redirect_stderr(log_file):
                print('-------- Starting job')
                job.run()

    def query_jobs(self, **query):
        yield from self.query_jobs_with_class(Job, **query)

    def query_jobs_with_class(self, job_cls, **query):
        for job_dir in self.output_dir.iterdir():
            if job_dir.is_dir():
                try:
                    job = job_cls.from_directory(job_dir)
                except FileNotFoundError:
                    continue
                for key, value_or_conditional in query.items():
                    actual = getattr(job, key)
                    if not _test_condition(actual, value_or_conditional):
                        break
                else:  # Executed if loop runs to its end without hitting break, or if query is empty
                    yield job


    def job_file(self, job, subpath):
        return self.output_dir / job.hash / subpath

    def shared(self, subpath):
        shared_dir = self.output_dir / 'shared'
        if not shared_dir.exists():
            shared_dir.mkdir(parents=True)

        return shared_dir / subpath

    def _setup_job(self, job):
        job.context = self
        job_dir = self.output_dir / job.hash
        job_dir.mkdir(exist_ok=True, parents=True)

        with (job_dir / 'params.json').open('w') as f:
            json.dump(job._params, f)

    def _check_and_write_config(self, config):
        config_path = self.output_dir / 'config.json'
        if config_path.exists():
            with config_path.open('r') as f:
                old_config = json.load(f)
                old_hash = Job.create_hash(old_config)
                new_hash = Job.create_hash(config)
                if not old_hash == new_hash:
                    all_keys = set(config.keys()).union(set(old_config.keys()))
                    changes = []
                    for key in all_keys:
                        old_val = old_config.get(key, None)
                        new_val = config.get(key, None)
                        if not old_val == new_val:
                            changes.append((key, old_val, new_val))
                    change_str = ', '.join(f'{key}: {old}->{new}' for key, old, new in changes)
                    raise ValueError(f"Experiment context configuration has changed. [{change_str}]")
        else:
            with config_path.open('w') as f:
                json.dump(config, f, sort_keys=True)


class Job:
    @staticmethod
    def create_hash(param_dict):
        json_data = json.dumps(param_dict, sort_keys=True).encode('utf8')
        return hashlib.sha256(json_data).hexdigest(), json_data

    @classmethod
    def from_directory(cls, directory):
        with (directory / 'params.json').open('r') as f:
            param_data = json.load(f)
            return cls(**param_data)

    def __init__(self, **params):
        self._params = params
        self.__dict__.update(params)
        self.hash, self._hashdata = Job.create_hash(params)
        self.context = None

    def path(self, subpath):
        "Path object for subpath for the current job"
        return self.context.job_file(self, subpath)

    def is_done(self):
        raise NotImplemented("Job has not implemented is_done function")

