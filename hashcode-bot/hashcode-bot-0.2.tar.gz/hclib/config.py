from pathlib import Path

import attr
import yaml


@attr.s
class ConfigV1:
    _path = attr.ib()
    _doc = attr.ib()

    @classmethod
    def _load(cls, path, doc):
        return cls(path, doc)

    def _get(self, key, default):
        val = self._doc
        for part in key.split('.'):
            try:
                val = val[part]
            except (TypeError, KeyError):
                return default
        return val

    @property
    def datafile_path(self):
        return self._get('paths.datafile', '.hashcode.json')

    @property
    def statement_path(self):
        return self._get('paths.statement', 'statement.pdf')

    @property
    def datasets_path(self):
        return self._get('paths.datasets', 'input')

    @property
    def runs_path(self):
        return self._get('paths.runs', 'output')

    @property
    def code_path(self):
        return self._get('paths.code', 'code')

    @property
    def judge_username(self):
        return self._get('judge.username', 'DEFAULT')

    @property
    def passenv(self):
        return tuple(self._get('run.passenv', (
            'LC_CTYPE',
            'TMPDIR',
            'LC_ALL',
            'LANG',
        )))

    @property
    def command(self):
        command = self._get('run.command', None)
        if command is None:
            raise ValueError('Command not configured')
        return command


SUPPORTED_VERSIONS = {
    '1': ConfigV1,
}

DEFAULT_CONFIG_FILENAME = 'hashcode.yml'

DEFAULT_CONFIG_CONTENT = """
version: "1"

run:
  # Will be executed in the directory pointed to by `paths.code`
  command: "python run.py {infile} {outfile} {metafile}"
""".lstrip()


def readconf(path):
    path = Path(path)
    if path.exists():
        with path.open() as fh:
            doc = yaml.load(fh)
    else:
        doc = yaml.load(DEFAULT_CONFIG_CONTENT)
    config_ver = doc.get('version')
    config_cls = SUPPORTED_VERSIONS.get(config_ver)
    if not config_cls:
        raise RuntimeError(f'Unsupported config version: {config_ver}')
    return config_cls._load(path, doc)


def dumpconf(conf, path=None):
    if path is None:
        path = conf._path
    with path.open('w') as fh:
        yaml.dump(conf._doc, fh)
