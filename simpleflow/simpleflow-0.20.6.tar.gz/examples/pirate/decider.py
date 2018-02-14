from simpleflow import activity, futures, Workflow

# decorator for all activities
def pirate_activity(func):
    return activity.with_attribute(
        task_list="pirate",
        version="1.0",
        idempotent=True,
    )


@pirate_activity
def find_or_steal_money():
    pass

def build_boat():
    pass

class PirateBusiness(Workflow):
    task_list = "captain"
    version = "1.0"

    def run(self):
        pass
