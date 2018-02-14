from xldeploy.service.tasks import TaskService


class Task(object):

    def __init__(self, task_id, http_client):
        self.task_id = task_id
        self.task_service = TaskService(http_client)

    def get_task(self):
        return self.task_service.get_task(self.task_id)

    def get_steps(self, block_path):
        return self.task_service.get_steps(self.task_id, block_path)

    def start(self):
        self.task_service.start(self.task_id)

    def schedule(self, time):
        self.task_service.schedule(self.task_id, time)

    def stop(self):
        self.task_service.stop(self.task_id)

    def abort(self):
        self.task_service.abort(self.task_id)

    def cancel(self):
        self.task_service.cancel(self.task_id)

    def archive(self, task_id):
        self.task_service.archive(self.task_id)
