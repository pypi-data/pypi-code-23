import json
import uuid
from pathlib import Path

from spooler.connectors.base import Connector
from spooler.task import Task


class FSConnector(Connector):

    def __init__(self, directory):
        if isinstance(directory, str):
            directory = Path(directory)
        self.directory = directory

    def get_available_tasks(self):
        for path in self.directory.iterdir():
            if not path.is_file():
                continue
            with path.open() as fp:
                payload = fp.read()
            data = json.loads(payload)
            task = Task.from_name(data.pop("callback"), *data.pop("args"),
                                  **data.pop("kwargs"))
            task.uid = uuid.UUID(path.stem)
            yield task

    def add_task(self, task):
        task.uid = uuid.uuid4()
        path = self.get_taskfile(task.uid)
        payload = {"callback": task.get_callback_name(), "args": task.args,
                   "kwargs": task.kwargs}
        with path.open('w') as fp:
            fp.write(json.dumps(payload))
        return task

    def mark_tasks_done(self, *ids):
        for id in ids:
            path = self.get_taskfile(id)
            path.unlink()

    def get_taskfile(self, id):
        return self.directory / (str(id) + ".json")
