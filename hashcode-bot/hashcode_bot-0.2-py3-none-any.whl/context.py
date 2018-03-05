import os
import enum
import json
import shlex
import subprocess
import random
import shutil
from functools import total_ordering

import attr
import click
import keyring

from .utils import archive_dir
from .config import readconf, DEFAULT_CONFIG_FILENAME, DEFAULT_CONFIG_CONTENT


@attr.s(hash=True)
class Context:
    root = attr.ib()
    config_filename = attr.ib(default=DEFAULT_CONFIG_FILENAME)
    config = attr.ib(init=False, repr=False, cmp=False)
    _keyring = attr.ib(init=False, default=keyring, repr=False, cmp=False)
    _judge = attr.ib(init=False, default=None, cmp=False)
    _data = attr.ib(init=False, cmp=False)
    _round = attr.ib(init=False, default=None, cmp=False)

    def __attrs_post_init__(self):
        self.config = readconf(self.root / self.config_filename)

        credentials = self.get_password(self.config.judge_username)
        if credentials:
            from . import judge
            credentials = judge.unserialize_credentials(credentials)
            resource = judge.build_hashcode_resource(credentials)
            self._judge = judge.JudgeClient(resource)

    @classmethod
    def init(cls, root, *, config_filename=DEFAULT_CONFIG_FILENAME, **kwargs):
        root.mkdir(exist_ok=True, parents=True)

        with root.joinpath(config_filename).open('w') as fh:
            fh.write(DEFAULT_CONFIG_CONTENT)

        return cls(root=root, config_filename=config_filename, **kwargs)

    @property
    def judge(self):
        if self._judge is None:
            raise click.UsageError(
                'You are not authenticated to the judge system.\n'
                'You might need to run the \'login\' command to do so.'
            )
        return self._judge

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self.reload_data()
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def round(self):
        if self._round is None and 'round_id' in self.data:
            self._round = self.judge.round(self.data['round_id'])
        return self._round

    def set_password(self, key, secret):
        return self._keyring.set_password('hashcode-bot', key, secret)

    def get_password(self, key):
        return self._keyring.get_password('hashcode-bot', key)

    def reload_data(self):
        data_path = self.root / self.config.datafile_path
        if data_path.exists():
            with data_path.open() as fh:
                self._data = json.load(fh)
        else:
            self._data = {}

    def persist_data(self):
        if not hasattr(self, '_data'):
            # Nothing to persist
            return
        datafile_path = self.root / self.config.datafile_path
        datafile_path.parent.mkdir(exist_ok=True, parents=True)
        with datafile_path.open('w') as fh:
            json.dump(self._data, fh, indent=4)
            fh.write('\n')

    def init_next_run(self):
        runs_dir = self.root / self.config.runs_path
        last_run_id = max(
            (int(d.stem) for d in runs_dir.glob('[0-9]*')),
            default=None,
        )
        next_run_id = last_run_id + 1 if last_run_id is not None else 0
        return Run.init(context=self, id=next_run_id)

    def get_run(self, run_id):
        run_dir = self.root / self.config.runs_path / str(run_id)
        assert run_dir.exists()
        return Run(context=self, root=run_dir, id=run_id)

    def last_run(self):
        runs_dir = self.root / self.config.runs_path
        last_run_path = max(
            runs_dir.glob('[0-9]*'),
            default=None,
            key=lambda d: int(d.stem),
        )
        return Run(context=self, root=last_run_path, id=last_run_path.stem)

    def reset_runs(self):
        runs_dir = self.root / self.config.runs_path
        for d in runs_dir.glob('[0-9]*'):
            shutil.rmtree(d)

    @property
    def datasets(self):
        return sorted((self.root / self.config.datasets_path).iterdir())

    def register_highscore(self, result):
        self.data.setdefault('highscores', {})[result.dataset.stem] = (
            result.score,
            result.run.id,
        )

    @property
    def highscore(self):
        return sum(
            (h[0] for h in self.data.get('highscores', {}).values()),
            0,
        )

    def dataset_highscore(self, dataset):
        highscore, run_id = (
            self.data
            .get('highscores', {})
            .get(dataset.stem, (0, None))
        )
        if run_id is not None:
            root = self.root / self.config.runs_path / str(run_id)
            run = Run(self, root, run_id)
            return run.load_result(dataset)
        else:
            return None


@attr.s(hash=True)
class Run:
    context = attr.ib(repr=False)
    root = attr.ib(repr=False)
    id = attr.ib(convert=attr.converters.optional(int), default=None)
    environ = attr.ib(default=None, cmp=False)

    def __attrs_post_init__(self):
        if self.environ is None:
            datapath = self.root / 'data.json'
            if datapath.exists():
                data = json.loads(datapath.read_text())
                self.environ = data['environ']
            else:
                env = {
                    k: os.environ[k]
                    for k in self.context.config.passenv
                    if k in os.environ
                }
                if 'RANDOM_SEED' in os.environ:
                    env['RANDOM_SEED'] = os.environ['RANDOM_SEED']
                else:
                    env['RANDOM_SEED'] = str(random.randrange(10 ** 10))
                self.environ = env

    @classmethod
    def init(cls, context, id):
        root = context.root / context.config.runs_path / str(id)
        root.mkdir()
        return cls(context, root, id)

    def persist_data(self, results):
        scores = {
            r.dataset.stem: r.score
            for r in results if r.succeeded()
        }
        with (self.root / 'data.json').open('w') as fh:
            json.dump({
                'environ': self.environ,
                'total_score': sum(scores.values(), 0),
                'scores': scores,
            }, fh, indent=4)
            fh.write('\n')

    def archive_code(self):
        code_dir = self.context.root / self.context.config.code_path
        with self.root.joinpath('code.zip').open('wb') as fh:
            archive_dir(fh, code_dir)

    def run_dataset(self, dataset, *, capture_output=True):
        base = self.root / dataset.stem
        outfile, metafile, stdout, stderr = [
            base.with_suffix(s)
            for s in ('.out', '.meta', '.stdout', '.stderr')
        ]
        command = self.context.config.command.format(
            infile=dataset,
            outfile=outfile,
            metafile=metafile,
        )

        with stdout.open('w') as stdout_fh, stderr.open('w') as stderr_fh:
            if not capture_output:
                stdout_fh = None
                stderr_fh = None
            proc = subprocess.Popen(
                args=shlex.split(command),
                stdout=stdout_fh,
                stderr=stderr_fh,
                cwd=self.context.root / self.context.config.code_path,
                env=self.environ,
            )
            try:
                retcode = proc.wait()
            except KeyboardInterrupt:
                try:
                    retcode = proc.wait()
                except KeyboardInterrupt:
                    proc.kill()
                    retcode = None

        if metafile.exists():
            meta = json.loads(metafile.read_text())
        else:
            meta = {}

        if retcode == 0 and meta and outfile.exists():
            status = RunStatus.SUCCEEDED
        elif retcode is None:
            status = RunStatus.INTERRUPTED
        else:
            status = RunStatus.FAILED

        result = DatasetRunResult(
            run=self,
            dataset=dataset,
            status=status,
            meta=meta,
        )
        result.persist()
        return result

    def upload_sources(self):
        return self.context.judge.upload(self.root.joinpath('code.zip'))

    def load_result(self, dataset):
        return DatasetRunResult.load(self, dataset)


class RunStatus(enum.IntEnum):
    SUCCEEDED = 1
    FAILED = 2
    INTERRUPTED = 3


@attr.s(cmp=False)
@total_ordering
class DatasetRunResult:
    run = attr.ib()
    dataset = attr.ib()
    status = attr.ib()
    meta = attr.ib()

    def __eq__(self, other):
        return (
            isinstance(other, DatasetRunResult)
            and self.run.id == other.run.id
            and self.dataset == other.dataset
            and self.score == other.score
        )

    def __gt__(self, other):
        if not isinstance(other, DatasetRunResult):
            return NotImplemented
        if self.dataset != other.dataset:
            return NotImplemented
        if not self.succeeded() or not other.succeeded():
            return NotImplemented
        return (self.score, other.run.id) > (other.score, self.run.id)

    @classmethod
    def load(cls, run, dataset):
        result = (run.root / dataset.stem).with_suffix('.result')
        if not result.exists():
            return None
        result = json.loads(result.read_text())
        meta = (run.root / dataset.stem).with_suffix('.meta')
        meta = json.loads(meta.read_text())
        return cls(
            run=run,
            dataset=dataset,
            status=RunStatus(result['status']),
            meta=meta,
        )

    def persist(self):
        datafile = (self.run.root / self.dataset.stem).with_suffix('.result')
        datafile.write_text(json.dumps({
            'status': self.status.value,
        }))

    def succeeded(self):
        return self.status == RunStatus.SUCCEEDED

    def failed(self):
        return self.status == RunStatus.FAILED

    def interrupted(self):
        return self.status == RunStatus.INTERRUPTED

    @property
    def score(self):
        return self.meta.get('score')

    @property
    def error_log_path(self):
        return (self.run.root / self.dataset.stem).with_suffix('.stderr')

    def is_highscore(self):
        highscore = self.run.context.highscore(self.dataset)
        if not highscore:
            return True

        return self >= highscore

    def submit(self, sources_blob_key=None):
        if sources_blob_key is None:
            sources_blob_key = self.run.upload_sources()

        dataset_ids = self.run.context.data.get('datasets')
        if not dataset_ids:
            dataset_ids = self.run.context.data['dataset_ids'] = {
                d.slug: d.id
                for d in self.run.context.round.data_sets
            }
            self.run.context.persist_data()

        dataset_id = dataset_ids[self.dataset.stem]
        solution_path = (self.run.root / self.dataset.stem).with_suffix('.out')
        solution_blob_key = self.run.context.judge.upload(solution_path)

        return self.run.context.judge.submit(
            dataset_id,
            sources_blob_key,
            solution_blob_key,
        )
