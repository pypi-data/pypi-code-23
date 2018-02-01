

def _load_xml(ps):
    with open(str(ps.raw_path), 'w'):
        pass


def _parse_xml(ps):
    with open(str(ps.parsed_path), 'w'):
        pass


def test_manager_workspace_update(tmpdir):
    from woger import WorkspaceManager, BaseAction, BasePathStructure

    class PathStructure(BasePathStructure):
        raw_path = 'data.xml'
        parsed_path = 'data.json'

    class Action(BaseAction):
        load_xml = 'load_data'
        parse_xml = 'parse_xml'

    root = str(tmpdir)
    manager = WorkspaceManager(root, PathStructure)
    assert manager.current() is None

    latest_finished_ws = manager.find_latest_finished(Action.parse_xml)
    assert latest_finished_ws is None

    timestamp = 1346134
    manager.create(timestamp)
    manager.target_latest()

    ws = manager.target()
    tracker = ws.track(Action.load_xml)

    if not tracker.finished():
        assert tracker.started() or tracker.failed() or tracker.undefined()
        with tracker:
            assert tracker.started()
            _load_xml(ws.path)
        assert tracker.finished()

    tracker = ws.track(Action.parse_xml)

    if not tracker.finished():
        with tracker:
            assert tracker.started()
            _parse_xml(ws.path)
        assert tracker.finished()

    assert manager.current() is None
    manager.update()
    assert manager.current() == manager.storage[timestamp] == manager.target()
