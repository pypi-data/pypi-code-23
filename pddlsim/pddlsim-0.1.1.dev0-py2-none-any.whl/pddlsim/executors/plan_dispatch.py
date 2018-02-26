from executor import Executor
import pddlsim.planner as planner

class PlanDispatcher(Executor):
    """docstring for PlanDispatcher."""
    def __init__(self):
        super(PlanDispatcher, self).__init__()
        self.steps = []

    def initilize(self,services):
        self.steps = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)

    def next_action(self):
        if len(self.steps) > 0:
            return self.steps.pop(0).lower()
        return None
