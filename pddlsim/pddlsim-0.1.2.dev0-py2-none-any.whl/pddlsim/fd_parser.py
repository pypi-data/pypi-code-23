
import external.fd.pddl as pddl
from six import iteritems, print_


class FDParser(object):
    def __init__(self, domain_path, problem_path):
        super(FDParser, self).__init__()
        self.domain_path = domain_path
        self.problem_path = problem_path
        self.task = pddl.pddl_file.open(problem_path, domain_path)
        self.objects = {obj.name: obj.type for obj in self.task.objects}
        self.actions = {action.name: Action(action)
                        for action in self.task.actions}
        # self.goals = [[subgoal.key for subgoal in goal.parts] for goal in self.task.goal]
        self.goals = self.task.goal[:]

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
    def get_entry(param_mapping, predicate):
        names = [x for x in predicate]
        entry = tuple([param_mapping[name][0] for name in names])
        return entry

    def test_condition(self, condition, mapping):
        if isinstance(condition, pddl.Literal):
            return condition.args in mapping[condition.predicate]
        if isinstance(condition, pddl.conditions.Conjunction):
            return all([self.test_condition(part, mapping) for part in condition.parts])
        if isinstance(condition, pddl.conditions.Disjunction):
            return any([self.test_condition(part, mapping) for part in condition.parts])

    def pd_to_strips_string(self, condition):
        if isinstance(condition, pddl.Literal):
            return "({} {})".format(condition.predicate, ' '.join(condition.args))
        if isinstance(condition, pddl.Conjunction):
            return "(and {})".format(' '.join(map(self.pd_to_strips_string, condition.parts)))
        if isinstance(condition, pddl.Disjunction):
            return "(or {})".format(' '.join(map(self.pd_to_strips_string, condition.parts)))

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


class Action(object):
    def __init__(self, action):
        self.name = action.name
        self.signature = [(obj.name, obj.type) for obj in action.parameters]
        self.addlist = []
        self.dellist = []
        for effect in action.effects:
            if effect.literal.negated:
                self.dellist.append(effect.literal.key)
            else:
                self.addlist.append(effect.literal.key)
        self.precondition = [Predicate.from_predicate(
            pred) for pred in action.precondition.parts]

    def action_string(self, dictionary):
        params = " ".join([dictionary[var[0]] for var in self.signature])
        return "(" + self.name + " " + params + ")"

    def entries_from_list(self, preds, param_mapping):
        return [(pred[0], FDParser.get_entry(param_mapping, pred[1])) for pred in preds]

    def to_delete(self, param_mapping):
        return self.entries_from_list(self.dellist, param_mapping)

    def to_add(self, param_mapping):
        return self.entries_from_list(self.addlist, param_mapping)

    def get_param_mapping(self, params):
        param_mapping = dict()
        for (name, param_type), obj in zip(self.signature, params):
            param_mapping[name] = obj
        return param_mapping


class Predicate(object):
    def __init__(self, name, signature):
        self.name = name
        self.signature = signature

    @staticmethod
    def from_predicate(predicate):
        return Predicate(predicate.predicate, predicate.args)

    def ground(self, dictionary):
        return tuple([dictionary[x][0] for x in self.signature])

    def test(self, param_mapping, state):
        return self.ground(param_mapping) in state[self.name]


class PreconditionFalseError(Exception):
    pass
