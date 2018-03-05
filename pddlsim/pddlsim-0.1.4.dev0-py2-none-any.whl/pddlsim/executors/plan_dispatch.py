from executor import Executor
import pddlsim.planner


class PlanDispatcher(Executor):

    """docstring for PlanDispatcher."""

    def __init__(self, planner=None):
        super(PlanDispatcher, self).__init__()
        self.steps = []
        self.planner = planner or pddlsim.planner.make_plan

    def initialize(self, services):
        self.steps = self.planner(
            services.pddl.domain_path, services.pddl.problem_path)

    def next_action(self):
        if len(self.steps) > 0:
            return self.steps.pop(0).lower()
        return None
