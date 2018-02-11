import json
from os import environ
from pathlib import Path


CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], 'codex')

try:
    with open(CONFIG_DIR / 'config.json') as f:
        config = json.load(f)

except FileNotFoundError:
    config = {}

VSCODE_EXECUTABLE = config.get('vscode_executable', 'code-oss')
