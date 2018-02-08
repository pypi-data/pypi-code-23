import ipdb
import json
import sys

from swf.models import History as BaseHistory
from simpleflow.history import History

raw = open("analysis_5239__22XbjU4pPeZLalYlxEuKedPf4MXreQxoiQeDi9ouZfR8w%3D.json").read()
all_events = json.loads(raw)["events"]
all_events = sorted(all_events, key=lambda x: x["eventId"])

# first ACTIVITY_TYPE_DOES_NOT_EXIST is at event 150, so let's try to figure out
# what happened at this point
events = [
    evt for evt in all_events
    if evt["eventId"] <= 152 # and "Activity" in evt["eventType"]
]

# raw history from "swf" module
base_history = BaseHistory.from_event_list(events)
first_failure = [e for e in base_history.events if e._id == 150][0]
print first_failure
print first_failure.raw

#sys.exit(0)

# simpleflow history
history = History(base_history)
history.parse()

ipdb.set_trace()
