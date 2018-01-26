import enum
import tempfile

import pytest


class _ParseException(Exception):
    pass


def _body(ws, Action):

    load_tracker = ws.track(Action.load_raw_xml)
    with load_tracker:
        assert load_tracker.started()
        assert not load_tracker.finished()
        assert not load_tracker.failed()

    assert load_tracker.finished()
    assert not load_tracker.started()
    assert not load_tracker.failed()

    parse_tracker = ws.track(Action.parse_xml)
    with pytest.raises(_ParseException):
        with parse_tracker:
            assert parse_tracker.started()
            assert not parse_tracker.failed()
            assert not parse_tracker.finished()
            assert load_tracker.finished()
            raise _ParseException()

    assert parse_tracker.failed()
    assert not parse_tracker.finished()
    assert not parse_tracker.started()
    assert load_tracker.finished()
    assert not load_tracker.started()
    assert not load_tracker.failed()


def test_manager_state_updates():
    from woger import Workspace, BaseAction, BasePathStructure

    @enum.unique
    class Action(BaseAction):
        load_raw_xml = 'load_raw_xml'
        parse_xml = 'parse_xml'

    class PathStructure(BasePathStructure):
        pass

    with tempfile.TemporaryDirectory() as root:
        ws = Workspace(root, PathStructure)
        _body(ws, Action)
