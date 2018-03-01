class Task:
    def __init__(self, id, name,queue_id):
        self.id = id
        self.name = name
        self.state = 0
        self.queue_id = queue_id
        self.task_parameters = []

    def set_state(self, state):
        if (self.state < state):
            self.state = state
