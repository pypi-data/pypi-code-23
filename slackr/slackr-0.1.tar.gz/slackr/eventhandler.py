import Cocoa
from datetime import datetime
import time
from connection import Connection

CONTEXT_SWITCH_TIME_INTERVAL = 1 #Time interval at which events are generated based on context switching
EVENT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

class EventHandler():

    def __init__(self):
        self.c = Connection()
        self.last_active_obj = Cocoa.NSWorkspace.sharedWorkspace().activeApplication()
        self.last_active_obj_name = self.last_active_obj['NSApplicationName']
        self.timestamp = datetime.now().strftime(EVENT_TIME_FORMAT)

    def getActiveObject(self):
        return Cocoa.NSWorkspace.sharedWorkspace().activeApplication()

    def eventFormatter(self):
        end_time = datetime.now().strftime(EVENT_TIME_FORMAT)
        delta = datetime.strptime(end_time, EVENT_TIME_FORMAT) - \
                datetime.strptime(self.timestamp, EVENT_TIME_FORMAT)
        event = {
            "timestamp": self.timestamp,
            "end_time": datetime.now().strftime(EVENT_TIME_FORMAT),
            "duration": delta.seconds,
            "name": self.last_active_obj_name,
            "path": self.last_active_obj['NSApplicationPath']
        }
        self.timestamp = datetime.now().strftime(EVENT_TIME_FORMAT)
        self.last_active_obj = self.getActiveObject()
        self.last_active_obj_name = self.last_active_obj['NSApplicationName']

        print event
        self.c.sendEventToElastic(event)

    def contextSwitchEvent(self):
        while True:
            current_active_app = self.getActiveObject()
            if current_active_app['NSApplicationName'] != self.last_active_obj_name:
                self.eventFormatter()

            time.sleep(CONTEXT_SWITCH_TIME_INTERVAL)