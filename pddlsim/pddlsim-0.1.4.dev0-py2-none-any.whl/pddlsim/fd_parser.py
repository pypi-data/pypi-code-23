
import external.fd.pddl as pddl
from six import iteritems, print_
import abc
from parser_independent import *


class FDParser(object):

    def __init__(self, domain_path, problem_path):
        super(FDParser, self).__init__()
        self.domain_path = domain_path
        self.problem_path = problem_path
        self.task = pddl.pddl_file.open(problem_path, domain_path)
        self.objects = {obj.name: obj.type for obj in self.task.objects}
        self.actions = {action.name: self.convert_action(action)
                        for action in self.task.actions}
        # self.goals = [[subgoal.key for subgoal in goal.parts] for goal in
        # self.task.goal]

        self.goals = [self.convert_condition(subgoal)
                      for subgoal in self.task.goal]

    def build_first_state(self):
        initial_state = self.task.init
        current_state = dict()
        for predicate in self.task.predicates:
            current_state[predicate.name] = set()
        for atom in initial_state:
            current_state[atom.key[0]].add(atom.key[1])
        return current_state

    def get_object(self, name):
        """ Get a object tuple for a name """
        if name in self.objects:
            return (name, self.objects[name])

    def get_signature(self, original_signature):
        return tuple([self.get_object(x[0]) for x in original_signature])

    def get_goals(self):
        return self.goals

    def get_action(self, action_name):
        # return self.domain.actions[action_name]
        return self.actions[action_name]

    @staticmethod
    def convert_condition(condition):
        if isinstance(condition, pddl.Literal):
            return Literal(condition.predicate, condition.args)
        sub_conditions = [FDParser.convert_condition(sub_condition)
                          for sub_condition in condition.parts]
        if isinstance(condition, pddl.Conjunction):
            return Conjunction(sub_conditions)
        if isinstance(condition, pddl.Disjunction):
            return Disjunction(sub_conditions)

    @staticmethod
    def convert_action(action):
        name = action.name
        signature = [(obj.name, obj.type) for obj in action.parameters]
        addlist = []
        dellist = []
        for effect in action.effects:
            if effect.literal.negated:
                dellist.append(effect.literal.key)
            else:
                addlist.append(effect.literal.key)
        precondition = [Predicate(pred.predicate, pred.args)
                        for pred in action.precondition.parts]
        return Action(action.name, signature, addlist, dellist, precondition)

    def test_condition(self, condition, mapping):
        return condition.test(mapping)

    def pd_to_strips_string(self, condition):
        return condition.accept(StripsStringVisitor())

    def predicates_from_state(self, state):
        return [("(%s %s)" % (predicate_name, " ".join(map(str, pred)))) for predicate_name, predicate_set in state.iteritems() for pred in predicate_set if predicate_name != '=']

    def generate_problem(self, path, state, new_goal):
        predicates = self.predicates_from_state(state)
        goal = self.pd_to_strips_string(new_goal)
        # goal = self.tuples_to_string(new_goal)
        with open(path, 'w') as f:
            f.write('''
    (define (problem ''' + self.task.task_name + ''')
    (:domain  ''' + self.task.domain_name + ''')
    (:objects
        ''')
            for t in self.objects.keys():
                f.write('\n\t' + t)
            f.write(''')
(:init
''')
            f.write('\t' + '\n\t'.join(predicates))
            f.write('''
            )
    (:goal
        ''' + goal + '''
        )
    )
    ''')

    def apply_action_to_state(self, action_sig, state, check_preconditions=True):

        action_sig = action_sig.strip('()').lower()
        parts = action_sig.split(' ')
        action_name = parts[0]
        param_names = parts[1:]

        action = self.get_action(action_name)
        params = map(self.get_object, param_names)

        param_mapping = action.get_param_mapping(params)

        if check_preconditions:
            for precondition in action.precondition:
                if not precondition.test(param_mapping, state):
                    raise PreconditionFalseError()

        for (predicate_name, entry) in action.to_delete(param_mapping):
            predicate_set = state[predicate_name]
            if entry in predicate_set:
                predicate_set.remove(entry)

        for (predicate_name, entry) in action.to_add(param_mapping):
            state[predicate_name].add(entry)

    def copy_state(self, state):
        return {name: set(entries) for name, entries in state.items()}
