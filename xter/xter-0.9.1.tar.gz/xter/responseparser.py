import json

from xter.command import Command
from xter.task import Task


class TaskQueueParser:
    def parse(self, taskqueue):
        if 'task' in taskqueue:
            id = taskqueue['task']['id']
            name = taskqueue['task']['name']
            queue_id = taskqueue['id']
            task = Task(id, name,queue_id)
            return task
        return None


class CommandParser:
    def parse(self, queue):
        commands = []
        commands_data = queue['task']['command_list']
        for command_data in commands_data:
            command = self.parse_command_data(command_data)
            is_valid = command.is_valid()
            if is_valid:
                commands.append(command)

        return commands

    def parse_command_data(self, command_data):
        command = Command()
        command_properties = command_data['json_text']
        if command_properties:
            command_properties = json.loads(command_properties)
            command.name = command_properties['name']
            command.parameters = command_properties['parameters']

        return command


class ResponseParser:
    task_queue_parser = TaskQueueParser()
    command_parser = CommandParser()

    def parse(self, data):
        tasks = []
        for queue in data:
            task = self.task_queue_parser.parse(queue)
            if task == None:
                continue
            commands = self.command_parser.parse(queue)
            task.commands = commands
            tasks.append(task)

        return tasks
