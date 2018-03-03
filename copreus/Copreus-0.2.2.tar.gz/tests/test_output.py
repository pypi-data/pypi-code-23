import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import _thread
from time import sleep

from copreus.drivers.output import Output
from tests.tools import send_to_topic, get_topics_sub, get_mqtt_translations


filename = 'config_output.yaml'

def loop(topics, cmds):
    sleep(2)
    topic = topics["closed"]
    cmd_true = cmds["closed-true"]
    cmd_false = cmds["closed-false"]
    state = 0
    while 1:
        state = (state + 1) % 2
        if state:
            cmd = cmd_false
        else:
            cmd = cmd_true
        send_to_topic(filename, topic, cmd)
        sleep(1)


subs = get_topics_sub(filename)
cmds = get_mqtt_translations(filename)
_loop_thread = _thread.start_new_thread(loop, (subs,cmds,))
Output.standalone(('-c', filename,'-v'))

