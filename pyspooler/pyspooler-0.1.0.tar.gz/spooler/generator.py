class TaskGenerator:

    def __init__(self, connector, callback):
        self.connector = connector
        self.callback = callback

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def spool(self, *args, **kwargs):
        return self.connector.create_task(self.callback, *args, **kwargs)
