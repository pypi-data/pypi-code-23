import requests
from time import sleep

from xter import responseparser
from xter.commanddispatcher import CommandDispatcher
from xter.commandlistener import CommandListener
from xter.responseparser import ResponseParser

base_api_url = 'http://commander.itscoding.ch/'


class Commander():
    def __init__(self, command_dispatcher, api_url=''):
        self.command_dispatcher = command_dispatcher
        self.responseparser = ResponseParser()
        self.api_url = base_api_url
        if api_url:
            self.api_url = api_url

    def run(self):
        while True:
            data = requests.get(self.api_url + '/taskqueues')
            data = data.json()
            tasks = self.responseparser.parse(data)
            if tasks != []:
                for task in tasks:
                    for command in task.commands:
                        state = self.command_dispatcher.dispatch_command(command,task.task_parameters)
                        task.set_state(state)
                if task.state > 2:
                    task.state = 2
                requests.put(self.api_url + '/taskqueues/' + str(task.queue_id), {'state': task.state})
            sleep(1)
