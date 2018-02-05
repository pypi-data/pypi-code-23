class TaskService:

    __path = "/tasks/v2"

    def __init__(self, http_client):
        self.http_client = http_client

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def get_task(self, task_id):
        return self.http_client.get(path=self.get_path(task_id))

    def get_steps(self, task_id, block_path):
        return self.http_client.get(path=self.get_path(task_id, "block", block_path, "step"))

    def start(self, task_id):
        response = self.http_client.post(path=self.get_path(task_id, "start"))

    def schedule(self, task_id, time):
        params = {"time": time}
        response = self.http_client.post(path=self.get_path(task_id, "schedule"), params=params)

    def stop(self, task_id):
        response = self.http_client.post(path=self.get_path(task_id, "stop"))

    def abort(self, task_id):
        response = self.http_client.post(path=self.get_path(task_id, "abort"))

    def cancel(self, task_id):
        response = self.http_client.delete(path=self.get_path(task_id))

    def archive(self, task_id):
        response = self.http_client.post(path=self.get_path(task_id, "archive"))