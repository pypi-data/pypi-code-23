# Copyright 2016 - Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from collections import namedtuple
from collections import OrderedDict
import copy
import re
import time

from oslo_log import log

from vitrage.common.constants import EdgeProperties as EProps
from vitrage.common.constants import VertexProperties as VProps
from vitrage.common.utils import recursive_keypairs
from vitrage.datasources.listener_service import defaultdict
from vitrage.entity_graph.mappings.datasource_info_mapper \
    import DatasourceInfoMapper
from vitrage.evaluator.actions.action_executor import ActionExecutor
from vitrage.evaluator.actions.base import ActionMode
from vitrage.evaluator.actions.base import ActionType
import vitrage.evaluator.actions.priority_tools as pt
from vitrage.evaluator.base import is_function
from vitrage.evaluator.template_data import ActionSpecs
from vitrage.evaluator.template_data import EdgeDescription
from vitrage.evaluator.template_schema_factory import TemplateSchemaFactory
from vitrage.graph.algo_driver.algorithm import Mapping
from vitrage.graph.algo_driver.sub_graph_matching import \
    NEG_CONDITION
from vitrage.graph.driver import Vertex
from vitrage import storage

LOG = log.getLogger(__name__)

# Entry containing action info.
# specs - ActionSpecs
# mode - DO or UNDO (the action)
# action_id - the action id in scenario_repository
# Trigger_id  - a unique identifier per match in graph (i.e., the subgraph
# that matched the action in the spec) for the specific action.
ActionInfo = \
    namedtuple('ActionInfo', ['specs', 'mode', 'action_id', 'trigger_id'])

TARGET = 'target'
SOURCE = 'source'


class ScenarioEvaluator(object):

    def __init__(self,
                 conf,
                 e_graph,
                 scenario_repo,
                 actions_callback,
                 enabled=False):
        self._conf = conf
        self._entity_graph = e_graph
        self._db_connection = storage.get_connection_from_config(self._conf)
        self._scenario_repo = scenario_repo
        self._action_executor = ActionExecutor(self._conf, actions_callback)
        self._entity_graph.subscribe(self.process_event)
        self._active_actions_tracker = ActiveActionsTracker(
            self._conf, self._db_connection)
        self.enabled = enabled
        self.connected_component_cache = defaultdict(dict)

    @property
    def scenario_repo(self):
        return self._scenario_repo

    @scenario_repo.setter
    def scenario_repo(self, scenario_repo):
        self._scenario_repo = scenario_repo

    def run_evaluator(self, action_mode=ActionMode.DO):
        self.enabled = True
        vertices = self._entity_graph.get_vertices()
        start_time = time.time()
        for vertex in vertices:
            if action_mode == ActionMode.DO:
                self.process_event(None, vertex, True)
            elif action_mode == ActionMode.UNDO:
                self.process_event(vertex, None, True)
        LOG.info(
            'Run %s Evaluator on %s items - took %s',
            action_mode, str(len(vertices)), str(time.time() - start_time))

    def process_event(self, before, current, is_vertex, *args, **kwargs):
        """Notification of a change in the entity graph.

        :param is_vertex:
        :param before: The graph element (vertex or edge) prior to the
        change that happened. None if the element was just created.
        :param current: The graph element (vertex or edge) after the
        change that happened. Deleted elements should arrive with the
        vitrage_is_deleted property set to True
        """

        if not self.enabled:
            LOG.debug("Process event disabled")
            return

        LOG.debug('Process event - starting')
        LOG.debug("Element before event: %s, Current element: %s",
                  str(before),
                  str(current))

        before_scenarios = self._get_element_scenarios(before, is_vertex)
        current_scenarios = self._get_element_scenarios(current, is_vertex)
        before_scenarios, current_scenarios = \
            self._remove_overlap_scenarios(before_scenarios, current_scenarios)

        if len(before_scenarios) + len(current_scenarios):
            LOG.debug("Number of relevant scenarios found: undo = %s, do = %s",
                      str(len(before_scenarios)),
                      str(len(current_scenarios)))

        actions = self._process_and_get_actions(before,
                                                before_scenarios,
                                                ActionMode.UNDO)
        actions.extend(self._process_and_get_actions(current,
                                                     current_scenarios,
                                                     ActionMode.DO))
        actions_to_preform = []
        try:
            actions_to_preform = self._analyze_and_filter_actions(actions)
        except Exception as e:
            LOG.error("Evaluator error, will not execute actions %s",
                      str(actions))
            LOG.exception("Caught: %s", e)

        for action in actions_to_preform:
            LOG.info('Action: %s', self._action_str(action))
            self._action_executor.execute(action.specs, action.mode)

        LOG.debug('Process event - completed')

    def _get_element_scenarios(self, element, is_vertex):
        if not element \
                or element.get(VProps.VITRAGE_IS_DELETED) \
                or element.get(EProps.VITRAGE_IS_DELETED):
            return []
        elif is_vertex:
            return self._scenario_repo.get_scenarios_by_vertex(element)
        else:  # is edge
            edge_desc = self._get_edge_description(element)
            return self._scenario_repo.get_scenarios_by_edge(edge_desc)

    def _get_edge_description(self, element):
        source = self._entity_graph.get_vertex(element.source_id)
        target = self._entity_graph.get_vertex(element.target_id)
        edge_desc = EdgeDescription(element, source, target)
        return edge_desc

    @staticmethod
    def _remove_overlap_scenarios(before, current):
        intersection = list(filter(lambda x: x in before, current))
        before = list(filter(lambda x: x not in intersection, before))
        current = list(filter(lambda x: x not in intersection, current))
        return before, current

    def _process_and_get_actions(self, element, triggered_scenarios, mode):
        actions = []
        for triggered_scenario in triggered_scenarios:
            LOG.debug("Processing: %s", str(triggered_scenario))
            scenario_element = triggered_scenario[0]
            scenario = triggered_scenario[1]
            actions.extend(self._process_scenario(element,
                                                  scenario,
                                                  scenario_element,
                                                  mode))
        return actions

    def _process_scenario(self, element, scenario, scenario_elements, mode):
        if not isinstance(scenario_elements, list):
            scenario_elements = [scenario_elements]
        actions = []
        for action in scenario.actions:
            for scenario_element in scenario_elements:
                matches = self._evaluate_subgraphs(scenario.subgraphs,
                                                   element,
                                                   scenario_element,
                                                   action.targets[TARGET])

                actions.extend(self._get_actions_from_matches(scenario.version,
                                                              matches,
                                                              mode,
                                                              action))

        return actions

    def _evaluate_subgraphs(self,
                            subgraphs,
                            element,
                            scenario_element,
                            action_target):
        if isinstance(element, Vertex):
            return self._find_vertex_subgraph_matching(subgraphs,
                                                       action_target,
                                                       element,
                                                       scenario_element)
        else:
            return self._find_edge_subgraph_matching(subgraphs,
                                                     action_target,
                                                     element,
                                                     scenario_element)

    def _get_actions_from_matches(self,
                                  scenario_version,
                                  combined_matches,
                                  mode,
                                  action_spec):
        actions = []
        for is_switch_mode, matches in combined_matches:
            new_mode = mode
            if is_switch_mode:
                new_mode = ActionMode.UNDO \
                    if mode == ActionMode.DO else ActionMode.DO

            template_schema = \
                TemplateSchemaFactory().template_schema(scenario_version)

            for match in matches:
                match_action_spec = self._get_action_spec(action_spec, match)
                items_ids = \
                    [match_item[1].vertex_id for match_item in match.items()]
                match_hash = hash(tuple(sorted(items_ids)))
                self._evaluate_property_functions(template_schema, match,
                                                  match_action_spec.properties)

                actions.append(ActionInfo(match_action_spec, new_mode,
                                          match_action_spec.id, match_hash))

        return actions

    def _evaluate_property_functions(self, template_schema, match,
                                     action_props):
        """Evaluate the action properties, in case they contain functions

        In template version 2 we introduced functions, and specifically the
        get_attr function. This method evaluate its value and updates the
        action properties, before the action is being executed.

        Example:

        - action:
            action_type: execute_mistral
            properties:
              workflow: evacuate_vm
              input:
                vm_name: get_attr(instance1,name)
                force: false

        In this example, the method will iterate over 'properties', and then
        recursively over 'input', and for 'vm_name' it will replace the
        call for get_attr with the actual name of the VM. The input for the
        Mistral workflow will then be:
        vm_name: vm_1
        force: false

        """
        for key, value in action_props.items():
            if isinstance(value, dict):
                # Recursive call for a dictionary
                self._evaluate_property_functions(template_schema,
                                                  match, value)

            elif value is not None and is_function(value):
                # The value is a function
                func_and_args = re.split('[(),]', value)
                func_name = func_and_args.pop(0)
                args = [arg.strip() for arg in func_and_args if len(arg) > 0]

                # Get the function, execute it and update the property value
                func = template_schema.functions.get(func_name)
                action_props[key] = func(match, *args)

                LOG.debug('Changed property %s value from %s to %s', key,
                          value, action_props[key])

    @staticmethod
    def _get_action_spec(action_spec, match):
        targets = action_spec.targets
        real_items = {
            target: match[target_id] for target, target_id in targets.items()
        }
        return ActionSpecs(action_spec.id,
                           action_spec.type,
                           real_items,
                           action_spec.properties)

    @staticmethod
    def _generate_action_id(action_spec):
        """Generate a unique action id for the action

            BEWARE: The implementation of this function MUST NOT BE CHANGED!!

            The created hash is used for storing the active actions in the
            database. If changed, existing active actions can no longer be
            retrieved.
        """
        targets = [(k, v.vertex_id) for k, v in action_spec.targets.items()]
        return hash(
            (action_spec.type,
             tuple(sorted(targets)),
             tuple(sorted(recursive_keypairs(action_spec.properties))))
        )

    def _analyze_and_filter_actions(self, actions):
        LOG.debug("Actions before filtering: %s", actions)

        actions_to_perform = []
        for action_info in actions:
            if action_info.mode == ActionMode.DO:
                is_highest_score, exists = \
                    self._active_actions_tracker.calc_do_action(action_info)
                if is_highest_score and not exists:
                    actions_to_perform.append(action_info)
            elif action_info.mode == ActionMode.UNDO:
                is_highest_score, second_highest = \
                    self._active_actions_tracker.calc_undo_action(action_info)
                if is_highest_score:
                    # We should 'DO' the Second highest scored action so
                    # to override the existing dominant action.
                    # or, if there is no second highest scored action
                    # So we just 'UNDO' the existing dominant action
                    if second_highest:
                        action_to_perform = self._db_action_to_action_info(
                            second_highest)
                        actions_to_perform.append(action_to_perform)
                    else:

                        actions_to_perform.append(action_info)

        unique_ordered_actions = OrderedDict()
        for action in actions_to_perform:
            id_ = ScenarioEvaluator._generate_action_id(action.specs)
            unique_ordered_actions[id_] = action
        return unique_ordered_actions.values()

    def _find_vertex_subgraph_matching(self,
                                       subgraphs,
                                       action_target,
                                       vertex,
                                       scenario_vertex):
        """calculates subgraph matching for vertex

        iterates over all the subgraphs, and checks if the triggered vertex is
        in the same connected component as the action then run subgraph
        matching on the vertex and return its result, otherwise return an
        empty list of matches.
        """

        matches = []
        for subgraph in subgraphs:
            connected_component = self.get_connected_component(subgraph,
                                                               action_target)

            is_switch_mode = \
                connected_component.get_vertex(scenario_vertex.vertex_id)

            if is_switch_mode:
                initial_map = Mapping(scenario_vertex, vertex, True)
                mat = self._entity_graph.algo.sub_graph_matching(subgraph,
                                                                 initial_map)
                matches.append((False, mat))
            else:
                matches.append((True, []))
        return matches

    def _find_edge_subgraph_matching(self,
                                     subgraphs,
                                     action_target,
                                     edge,
                                     scenario_edge):
        """calculates subgraph matching for edge

        iterates over all the subgraphs, and checks if the triggered edge is a
        negative edge then mark it as deleted=false and negative=false so that
        subgraph matching on that edge will work correctly. after running
        subgraph matching, we need to remove the negative vertices that were
        added due to the change above.
        """

        matches = []
        for subgraph in subgraphs:
            subgraph_edge = subgraph.get_edge(scenario_edge.source.vertex_id,
                                              scenario_edge.target.vertex_id,
                                              scenario_edge.edge.label)
            if not subgraph_edge:
                continue

            is_switch_mode = subgraph_edge.get(NEG_CONDITION, False)

            connected_component = self.get_connected_component(subgraph,
                                                               action_target)
            # change the vitrage_is_deleted and negative_condition props to
            # false when is_switch_mode=true so that when we have an event on a
            # negative_condition=true edge it will find the correct subgraph
            self._switch_edge_negative_props(is_switch_mode, scenario_edge,
                                             subgraph, False)

            initial_map = Mapping(scenario_edge.edge, edge, False)
            curr_matches = \
                self._entity_graph.algo.sub_graph_matching(subgraph,
                                                           initial_map)

            # switch back to the original values
            self._switch_edge_negative_props(is_switch_mode, scenario_edge,
                                             subgraph, True)

            self._remove_negative_vertices_from_matches(curr_matches,
                                                        connected_component)

            matches.append((is_switch_mode, curr_matches))
        return matches

    def get_connected_component(self, subgraph, target):
        connected_component = self.connected_component_cache.get(
            id(subgraph), {}).get(id(target))
        if not connected_component:
            connected_component = subgraph.algo.graph_query_vertices(
                root_id=target,
                edge_query_dict={'!=': {NEG_CONDITION: True}})
            self.connected_component_cache[id(subgraph)][id(target)] = \
                connected_component
        return connected_component

    def _db_action_to_action_info(self, db_action):
        target = self._entity_graph.get_vertex(db_action.target_vertex_id)
        targets = {TARGET: target}
        if db_action.source_vertex_id:
            source = self._entity_graph.get_vertex(db_action.source_vertex_id)
            targets[SOURCE] = source
        scenario_action = self._scenario_repo.actions.get(db_action.action_id)
        properties = copy.copy(scenario_action.properties)
        action_specs = ActionSpecs(
            id=db_action.action_id,
            type=db_action.action_type,
            targets=targets,
            properties=properties,
        )
        action_info = ActionInfo(
            specs=action_specs,
            mode=ActionMode.DO,
            action_id=db_action.action_id,
            trigger_id=db_action.trigger,
        )
        return action_info

    @staticmethod
    def _switch_edge_negative_props(is_switch_mode,
                                    scenario_edge,
                                    subgraph,
                                    status):
        if is_switch_mode:
            scenario_edge.edge[NEG_CONDITION] = status
            scenario_edge.edge[EProps.VITRAGE_IS_DELETED] = status
            subgraph.update_edge(scenario_edge.edge)

    @staticmethod
    def _remove_negative_vertices_from_matches(matches, connected_component):
        for match in matches:
            ver_ids = [v.vertex_id for v in connected_component.get_vertices()]
            ver_to_remove = [id for id in match.keys() if id not in ver_ids]
            for v_id in ver_to_remove:
                del match[v_id]

    @staticmethod
    def _action_str(action):
        s = action.specs.targets.get(SOURCE, {}).get(VProps.VITRAGE_ID, '')
        t = action.specs.targets.get(TARGET, {}).get(VProps.VITRAGE_ID, '')
        return '%s %s \'%s\' targets (%s,%s)' % (action.mode.upper(),
                                                 action.specs.type,
                                                 action.action_id, s, t)


class ActiveActionsTracker(object):
    """Keeps track of all active actions and relative dominance/priority.

    Actions are organized according to resource-id and action details.

    Examples:

    - all set_state actions on a given resource are considered similar action
    regardless of state
    - all raise_alarm of type alarm_name on a given resource are considered
    similar action, regardless of severity

    Each action is assigned a score by mapping the value property to the
    priority defined in datasource values config.

    - Alarm: severity
    - Resource: state

    The score is used to determine which action in each group of similar
    actions to be executed next.
    """

    def __init__(self, conf, db_connection):
        info_mapper = DatasourceInfoMapper(conf)
        self._db = db_connection
        alarms_score = info_mapper.get_datasource_priorities('vitrage')
        all_scores = info_mapper.get_datasource_priorities()
        self._action_tools = {
            ActionType.SET_STATE: pt.SetStateTools(all_scores),
            ActionType.RAISE_ALARM: pt.RaiseAlarmTools(alarms_score),
            ActionType.ADD_CAUSAL_RELATIONSHIP: pt.BaselineTools,
            ActionType.MARK_DOWN: pt.BaselineTools,
            ActionType.EXECUTE_MISTRAL: pt.BaselineTools
        }

    def calc_do_action(self, action_info):
        """Add this action to active_actions table, if not exists

        return value to help decide if action should be performed
        Only a top scored action that is new should be performed
        :return: (is top score, is it already existing)
        """
        # TODO(idan_hefetz): DB read and write not in a transaction
        active_actions = self._query_similar_actions(action_info)
        exists = any(
            a.action_id == action_info.action_id and
            a.trigger == action_info.trigger_id for a in active_actions)
        if not exists:
            db_row = self._to_db_row(action_info)
            active_actions.append(db_row)
            LOG.debug("DB Insert active_actions %s", str(db_row))
            self._db.active_actions.create(db_row)

        return self._is_highest_score(active_actions, action_info), exists

    def calc_undo_action(self, action_info):
        """Delete this action form active_actions table, if exists

        return value to help decide if action should be performed
        A top scored action should be 'undone' if there is not a second action.
        If there is a second, it should now be 'done' and become the dominant
        :param action_info: action to delete
        :return: is_highest_score, second highest action if exists
        """
        # TODO(idan_hefetz): DB read and write not in a transaction
        active_actions = self._query_similar_actions(action_info)

        LOG.debug("DB delete active_actions %s %s",
                  action_info.action_id,
                  str(action_info.trigger_id))
        self._db.active_actions.delete(
            action_id=action_info.action_id,
            trigger=action_info.trigger_id)

        is_highest_score = self._is_highest_score(active_actions, action_info)
        if is_highest_score and len(active_actions) > 1:
            return is_highest_score, self._sort_db_actions(active_actions)[1]
        else:
            return is_highest_score, None

    def _to_db_row(self, action_info):
        source = action_info.specs.targets.get(SOURCE, {})
        target = action_info.specs.targets.get(TARGET, {})
        action_score = self._action_tools[action_info.specs.type].\
            get_score(action_info)
        extra_info = self._action_tools[action_info.specs.type].\
            get_extra_info(action_info.specs)
        return storage.sqlalchemy.models.ActiveAction(
            action_type=action_info.specs.type,
            extra_info=extra_info,
            source_vertex_id=source.get(VProps.VITRAGE_ID),
            target_vertex_id=target.get(VProps.VITRAGE_ID),
            action_id=action_info.action_id,
            trigger=action_info.trigger_id,
            score=action_score)

    def _query_similar_actions(self, action_info):
        """Query DB for all actions with same properties"""
        source = action_info.specs.targets.get(SOURCE, {})
        target = action_info.specs.targets.get(TARGET, {})
        extra_info = self._action_tools[action_info.specs.type].get_extra_info(
            action_info.specs)
        return self._db.active_actions.query(
            action_type=action_info.specs.type,
            extra_info=extra_info,
            source_vertex_id=source.get(VProps.VITRAGE_ID),
            target_vertex_id=target.get(VProps.VITRAGE_ID))

    @classmethod
    def _is_highest_score(cls, db_actions, action_info):
        """Get the top action from the list and compare to action_info

        Actions are sorted according to:
        score - primary, ascending
        created_at - secondary, descending
        """
        if not db_actions:
            return True
        highest_score_action = min(
            db_actions, key=lambda action: (-action.score, action.created_at))
        return highest_score_action.trigger == action_info.trigger_id and \
            highest_score_action.action_id == action_info.action_id

    @staticmethod
    def _sort_db_actions(db_actions):
        """Sort ActiveAction items by two fields

        score - primary, ascending
        created_at - secondary, descending
        """
        return sorted(
            db_actions,
            key=lambda action: (-action.score, action.created_at),
            reverse=False)
