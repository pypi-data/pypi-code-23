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

from oslo_config import cfg

from vitrage.common.constants import EntityCategory
from vitrage.common.constants import TemplateTypes as TType
from vitrage.common.constants import VertexProperties as VProps
from vitrage.evaluator.scenario_repository import ScenarioRepository
from vitrage.evaluator.template_validation.template_syntax_validator import \
    syntax_validation
from vitrage.graph import Vertex
from vitrage.tests import base
from vitrage.tests.functional.test_configuration import TestConfiguration
from vitrage.tests.mocks import utils
from vitrage.utils import file as file_utils


class ScenarioRepositoryTest(base.BaseTest, TestConfiguration):
    BASE_DIR = utils.get_resources_dir() + '/templates/general'
    OPTS = [
        cfg.StrOpt('templates_dir',
                   default=BASE_DIR,
                   ),
        cfg.StrOpt('equivalences_dir',
                   default='equivalences',
                   ),
    ]

    # noinspection PyPep8Naming
    @classmethod
    def setUpClass(cls):
        super(ScenarioRepositoryTest, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group='evaluator')
        cls.add_db(cls.conf)
        cls.add_templates(cls.conf.evaluator.templates_dir)
        templates_dir_path = cls.conf.evaluator.templates_dir
        cls.template_defs = file_utils.load_yaml_files(templates_dir_path)

        cls.scenario_repository = ScenarioRepository(cls.conf)

    def test_template_loader(self):

        # Test Action
        scenario_repository = ScenarioRepository(self.conf)

        # Test assertions
        self.assertIsNotNone(scenario_repository)
        self.assertEqual(
            2,
            len(scenario_repository.templates),
            'scenario_repository.templates should contain all valid templates')

    def test_init_scenario_repository(self):

        # Test Setup
        valid_template_counter = 0
        for template_definition in self.template_defs:
            syntax_validation_result = syntax_validation(template_definition)
            if syntax_validation_result.is_valid_config:
                valid_template_counter += 1

        # Test assertions
        self.assertIsNotNone(self.scenario_repository)

        scenario_templates = self.scenario_repository.templates
        # there is one bad template
        self.assertEqual(
            valid_template_counter,
            len(scenario_templates),
            'scenario_repository.templates should contain all valid templates')

        entity_equivalences = self.scenario_repository.entity_equivalences
        for entity_props, equivalence in entity_equivalences.items():
            # Example structure of entity_equivalences
            #   { A: (A, B, C),
            #     B: (A, B, C),
            #     C: (A, B, C)}
            # Verify entity itself is also included. It is not required, but
            # worth noting when handling equivalence
            self.assertTrue(entity_props in equivalence)
            for equivalent_props in equivalence:
                # Verify equivalent scenarios are present in repository
                self.assertTrue(equivalent_props in
                                self.scenario_repository.entity_scenarios)

    def test_get_scenario_by_edge(self):
        pass

    def test_get_scenario_by_entity(self):
        pass

    def test_add_template(self):
        pass


class RegExTemplateTest(base.BaseTest, TestConfiguration):

    BASE_DIR = utils.get_resources_dir() + '/templates/regex'
    OPTS = [
        cfg.StrOpt('templates_dir',
                   default=BASE_DIR)]

    @classmethod
    def setUpClass(cls):
        super(RegExTemplateTest, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group='evaluator')
        cls.add_db(cls.conf)
        cls.add_templates(cls.conf.evaluator.templates_dir)
        cls.scenario_repository = ScenarioRepository(cls.conf)

    def test_basic_regex(self):

        event_properties = {
            "time": 121354,
            "vitrage_type": "zabbix",
            "vitrage_category": "ALARM",
            "rawtext": "Interface virtual-0 down on {HOST.NAME}",
            "host": "some_host_kukoo"
        }
        event_vertex = Vertex(vertex_id="test_vertex",
                              properties=event_properties)
        relevant_scenarios = \
            self.scenario_repository.get_scenarios_by_vertex(
                event_vertex)
        self.assertEqual(1, len(relevant_scenarios))
        relevant_scenario = relevant_scenarios[0]
        self.assertEqual("zabbix_alarm_pass", relevant_scenario[0].vertex_id)

    def test_regex_with_exact_match(self):

        event_properties = {
            "time": 121354,
            "vitrage_type": "zabbix",
            "vitrage_category": "ALARM",
            "rawtext": "Public interface host43 down",
            "host": "some_host_kukoo"
        }
        event_vertex = Vertex(vertex_id="test_vertex",
                              properties=event_properties)
        relevant_scenarios = \
            self.scenario_repository.get_scenarios_by_vertex(
                event_vertex)
        self.assertEqual(1, len(relevant_scenarios))
        relevant_scenario = relevant_scenarios[0]
        self.assertEqual("exact_match", relevant_scenario[0].vertex_id)

    def test_basic_regex_with_no_match(self):

        event_properties = {
            "time": 121354,
            "vitrage_type": "zabbix",
            "vitrage_category": "ALARM",
            "rawtext": "No Match",
            "host": "some_host_kukoo"
        }
        event_vertex = Vertex(vertex_id="test_vertex",
                              properties=event_properties)
        relevant_scenarios = \
            self.scenario_repository.get_scenarios_by_vertex(
                event_vertex)
        self.assertEqual(0, len(relevant_scenarios))


class EquivalentScenarioTest(base.BaseTest, TestConfiguration):
    BASE_DIR = utils.get_resources_dir() + '/templates/equivalent_scenarios/'
    OPTS = [
        cfg.StrOpt('templates_dir',
                   default=BASE_DIR,
                   ),
        cfg.StrOpt('def_templates_dir',
                   default=(utils.get_resources_dir() +
                            '/templates/def_template_tests'),
                   ),
        cfg.StrOpt('equivalences_dir',
                   default=BASE_DIR + '/equivalences',),
    ]

    @classmethod
    def setUpClass(cls):
        super(EquivalentScenarioTest, cls).setUpClass()
        cls.conf = cfg.ConfigOpts()
        cls.conf.register_opts(cls.OPTS, group='evaluator')
        cls.add_db(cls.conf)
        cls.add_templates(cls.conf.evaluator.templates_dir)
        cls.add_templates(cls.conf.evaluator.equivalences_dir,
                          TType.EQUIVALENCE)
        cls.add_templates(cls.conf.evaluator.def_templates_dir,
                          TType.DEFINITION)
        cls.scenario_repository = ScenarioRepository(cls.conf)

    def test_expansion(self):
        entity_scenarios = self.scenario_repository.entity_scenarios
        for key, scenarios in entity_scenarios.items():
            if (VProps.VITRAGE_CATEGORY, EntityCategory.ALARM) in key:
                # scenarios expanded on the other alarm
                self.assertEqual(2, len(scenarios))
            if (VProps.VITRAGE_CATEGORY, EntityCategory.RESOURCE) in key:
                # Scenarios expanded on the two alarms. Each alarm is expanded
                # to two equivalent alarms. Thus 2 x 2 = 4 in total
                self.assertEqual(4, len(scenarios))
        # each relationship is expand to two. Thus 2 x 2 = 4 in total
        relationships = self.scenario_repository.relationship_scenarios.keys()
        self.assertEqual(4, len(relationships))
