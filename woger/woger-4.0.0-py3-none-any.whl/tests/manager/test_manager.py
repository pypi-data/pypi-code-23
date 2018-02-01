from itertools import starmap
from pathlib import Path

import os
from random import randint
import random
from typing import Iterable

import pytest


def test_manager_latest_workspace(tmpdir):
    from woger import WorkspaceManager, Workspace, BasePathStructure

    class OrderedWorkspace(Workspace):
        def __lt__(self, other):
            return self.state_path < other._state_path

    subdirs = ['134', '235', '9', '17']
    latest_id = 235

    root = str(tmpdir)

    for path in subdirs:
        os.makedirs(str(Path(root) / path), exist_ok=True)

    wm = WorkspaceManager(root, BasePathStructure, workspace_cls=OrderedWorkspace)

    assert wm.latest().id == latest_id


def test_manager_current_and_target(tmpdir):
    from woger import WorkspaceManager, BasePathStructure
    from woger.constants import _TARGET, _CURRENT, _STATE

    names = list(map(str, range(randint(50, 100), randint(950, 1000), 49)))
    random.shuffle(names)
    current, target = names[0], names[-1]
    contents = (
        '{{'
        '"{current_tag}": {current},'
        '"{target_tag}": {target}'
        '}}'
    ).format(
        target=target,
        current=current,
        target_tag=_TARGET,
        current_tag=_CURRENT,
    )

    root = Path(str(tmpdir))
    with open(str(root / _STATE), 'w') as f:
        f.write(contents)

    for name in names:
        os.makedirs(str(root / name), exist_ok=True)

    manager = WorkspaceManager(
        root,
        BasePathStructure,
    )

    assert manager.current().root == root / current
    assert manager.target().root == root / target


_paths = [
    '346',
    '134',
    '576',
]

_contents = [(
    '{"load_raw_xml":"finished","parse_xml": "finished"}',
    '{"load_raw_xml":"finished","parse_xml": "finished"}',
    '{"load_raw_xml": "finished","parse_xml": "started"}',
), (
    '{"load_raw_xml":"finished","parse_xml": "failed"}',
    '{"load_raw_xml": "started"}',
    '{"load_raw_xml": "finished","parse_xml": "started"}',
)]

_checks = [
    lambda ws: ws.id == 346,
    lambda ws: ws is None,
]


class _Meta:
    def __init__(self, path, contents):
        self.path = path
        self.contents = contents


@pytest.mark.parametrize('meta_list,check', [
    (list(starmap(_Meta, zip(_paths, _contents[i]))), _checks[i])
    for i
    in [0, 1]
])
def test_manager_search_latest_finished(meta_list: Iterable[_Meta], check, tmpdir):
    from woger import WorkspaceManager, BasePathStructure, BaseAction
    from woger.manager import _STATE

    root = Path(str(tmpdir))
    for meta in meta_list:
        os.makedirs(str(root / meta.path), exist_ok=True)
        path = root / meta.path / _STATE
        with open(str(path), 'w') as f:
            f.write(meta.contents)

    class Action(BaseAction):
        load_raw_xml = 'load_raw_xml'
        parse_xml = 'parse_xml'

    wm = WorkspaceManager(root, BasePathStructure)
    ws = wm.find_latest_finished(Action.parse_xml)

    print(wm.storage)
    assert check(ws)
