from executor import Executor
import pddlsim.planner


class MultipleGoalPlanDispatcher(Executor):

    """docstring for PlanDispatcher."""

    def __init__(self, planner=None):
        super(MultipleGoalPlanDispatcher, self).__init__()
        self.steps = []
        self.services = None
        self.planner = planner or pddlsim.planner.make_plan

    def initialize(self, services):
        self.services = services

    def next_action(self):
        if not self.steps and self.services.goal_tracking.uncompleted_goals:
            if self.services.goal_tracking.reached_all_goals():
                return None
            next_goal = self.services.goal_tracking.uncompleted_goals[-1]
            print next_goal
            # get only one goal
            next_problem = self.services.problem_generator.generate_problem(
                next_goal)
            self.steps = self.planner(
                self.services.pddl.domain_path, next_problem)

        if self.steps:
            return self.steps.pop(0).lower()

        return None
