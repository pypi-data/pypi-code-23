from pddlsim.successors.tracked_successor import TrackedSuccessor


class ValidActions():

    def __init__(self, valid_action_func):
        self.get = valid_action_func


class TrackedSuccessorValidActions():

    """
    Use the TrackedSuccessor to query for valid actions at the current state
    This successor is tracked because LAPKT needs to keep track of the state
    """

    def __init__(self, pddl, problem_generator, goal_tracking):
        if goal_tracking.has_multiple_goals():
            next_problem = problem_generator.generate_problem(
                goal_tracking.uncompleted_goals[0])
            self.successor = TrackedSuccessor(pddl.domain_path, next_problem)
        else:
            self.successor = TrackedSuccessor(
                pddl.domain_path, pddl.problem_path)

    def get(self):
        return map(str.lower, self.successor.next())

    def on_action(self, action_sig):
        if action_sig:
            self.successor.proceed(action_sig)


class PythonValidActions():

    """
    Python implemention for valid actions
    This is significantly less efficient than the TrackedSuccessor version
    """

    def __init__(self, simulator):
        self.simulator = simulator

    def get(self):
        possible_actions = []
        for (name, action) in self.simulator.parser.actions.items():
            for candidate in self.get_valid_candidates_for_action(action):
                possible_actions.append(action.action_string(candidate))
        return possible_actions

    def join_candidates(self, previous_candidates, new_candidates, p_indexes, n_indexes):
        shared_indexes = p_indexes.intersection(n_indexes)
        if previous_candidates is None:
            return new_candidates
        result = []
        for c1 in previous_candidates:
            for c2 in new_candidates:
                if all([c1[idx] == c2[idx] for idx in shared_indexes]):
                    merged = c1[:]
                    for idx in n_indexes:
                        merged[idx] = c2[idx]
                    result.append(merged)
        return result

    def indexed_candidate_to_dict(self, candidate, index_to_name):
        return {name[0]: candidate[idx] for idx, name in index_to_name.items()}

    def get_valid_candidates_for_action(self, action):
        '''
        Get all the valid parameters for a given action for the current state of the simulation
        '''
        objects = dict()
        signatures_to_match = {
            name: (idx, t) for idx, (name, t) in enumerate(action.signature)}
        index_to_name = {idx: name for idx,
                         name in enumerate(action.signature)}
        candidate_length = len(signatures_to_match)
        found = set()
        candidates = None
        # copy all preconditions
        for precondition in sorted(action.precondition, key=lambda x: len(self.simulator.state[x.name])):
            thruths = self.simulator.state[precondition.name]
            if len(thruths) == 0:
                return []
            # map from predicate index to candidate index
            dtypes = [(name, 'object') for name in precondition.signature]
            reverse_map = {idx: signatures_to_match[pred][0] for idx, pred in enumerate(
                precondition.signature)}
            indexes = reverse_map.values()
            overlap = len(found.intersection(indexes)) > 0
            precondition_candidates = []
            for entry in thruths:
                candidate = [None] * candidate_length
                for idx, param in enumerate(entry):
                    candidate[reverse_map[idx]] = param
                precondition_candidates.append(candidate)

            candidates = self.join_candidates(
                candidates, precondition_candidates, found, indexes)
            # print( candidates)
            found = found.union(indexes)

        return [self.indexed_candidate_to_dict(c, index_to_name) for c in candidates]

    def get_valid_candidates_for_action_original(self, action):
        '''
        Get all the valid parameters for a given action for the current state of the simulation
        '''
        objects = dict()
        candidates = []
        # copy all preconditions
        precondition_left = action.precondition[:]
        for (name, t) in action.signature:
            objects[name] = t

            # add all possible objects of the type
            matching_objects = self.simulator.parser.get_objects_of_type(t)

            # filter predicates that can be tested at this stage
            preconditions_to_test = []
            for precondition in precondition_left:
                if self.simulator.parser.has_all_objects(precondition, objects):
                    preconditions_to_test.append(precondition)
            for pre in preconditions_to_test:
                precondition_left.remove(pre)

            new_candidates = []
            if len(objects) == 1:
                for instance in matching_objects:
                    new_candidates.append({name: instance})
            else:
                for previous_candidate in candidates:
                    for instance in matching_objects:
                        candidate = previous_candidate.copy()
                        candidate[name] = instance
                        new_candidates.append(candidate)
            # maybe this can happed while building candidates
            for precondition in preconditions_to_test:
                new_candidates[:] = [c for c in new_candidates if self.simulator.test_predicate(
                    precondition.name, precondition.signature, c)]
                # new_candidates[:] = [c for c in new_candidates if
                # precondition.test(c, self.simulator.state)]

            candidates = new_candidates
        return candidates
