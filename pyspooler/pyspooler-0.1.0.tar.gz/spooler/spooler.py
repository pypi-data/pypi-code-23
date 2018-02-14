class Spooler(object):
    """Run tasks.

    :param connector: An instance of Connector.
    """
    def __init__(self, connector):
        self.connector = connector

    def consume_available(self):
        """Continuously iterate on tasks to run them."""
        for task in self.connector.get_available_tasks():
            task.execute()
            self.connector.mark_tasks_done(task.uid)

    def consume(self):
        self._stop = False
        while not self._stop:
            self.consume_available()

    def stop(self):
        self._stop = True
