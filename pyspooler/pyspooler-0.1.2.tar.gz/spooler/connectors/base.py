from spooler.task import Task
from spooler.generator import TaskGenerator


class Connector(object):

    def iter_tasks(self):
        """Iterate on tasks without stop."""
        pass

    def create_task(self, *args, **kwargs):
        """Create a task and add it into the connector."""
        args = list(args)
        callback = args.pop(0)
        task = Task(callback, *args, **kwargs)
        return self.add_task(task)

    def add_task(self, task):
        """Store a task into the connector."""
        pass

    def get_available_tasks(self):
        """Retrieve task ready to be executed from the connector."""
        pass

    def mark_tasks_done(self, ids):
        """Remove tasks from the connector."""
        pass

    def spoolable(self, f):
        """Decorate a function to make it a task generator."""
        return TaskGenerator(self, f)
