from spooler.connectors.file_system import FSConnector
from spooler.task import Task


def test_fs_connector():
    conn = FSConnector("/tmp/pyspooler")
    task = Task(print, 1, 2, 3)
    conn.add_task(task)
    assert task.uid in (task.uid for task in conn.get_available_tasks())
    conn.mark_tasks_done(task.uid)
    assert len(list(conn.get_available_tasks())) == 0
