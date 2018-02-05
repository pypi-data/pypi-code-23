import urllib2
import logging
import os
import copy

from datetime import datetime
from lxml import etree
from lxml.etree import ElementTree
from collections import Counter, OrderedDict

# Settings for the logger
from kadmos.utilities.general import dict_to_ord_dict, assert_dict_keys, make_camel_case
from kadmos.utilities.strings import find_between, find_until
from kadmos.utilities.xmls import get_uid_search_xpath, ExtendedElement

# Settings for the parser
parser = etree.XMLParser(remove_blank_text=True)

logger = logging.getLogger(__name__)

class CMDOWS(object):
    """Class for with various methods for checking and manipulating CMDOWS files"""

    # ----------------------------------------- #
    #    Initialization and check functions     #
    # ----------------------------------------- #
    def __init__(self, file_path=None, element=None):
        self.SINGLE_MULTI_OPTIONS = ['Single', 'Multiple']
        self.VERIFICATION_ELEMENTS = ['method', 'verifier', 'result', 'date', 'version']
        self.MODEL_DEFINITION_ELEMENTS = ['reference_data_set', 'analysis_method', 'fitting_method']
        self.DATA_EXCHANGE_SETTINGS_ELEMENTS = ['dataserver', 'urlsite', 'web_authentication_protocol', 'context',
                                                'folder', 'polling_time', 'max_iterations', 'time_out',
                                                'shared_file_policy', 'servermutex']
        self.ROLES_OPTIONS = ['architect', 'integrator', 'collaborative_engineer', 'tool_specialist', 'customer']
        if file_path:
            self.file = file_path
        if element is not None:
            self.root = ElementTree(element).getroot()
        if file_path and element is None:
            self.root = ElementTree(file=file_path, parser=parser).getroot()
        if not file_path and element is None:
            self.root = Element('cmdows')

    def version(self):
        """Method to retrieve the version of the CMDOWS file"""
        url_prefix = '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'
        version = self.root.attrib[url_prefix].split('/')[-2]
        version = str(version)
        return version

    def schema(self):
        """Method to retrieve a schema either belonging to the CMDOWS file"""
        version = self.version()
        try:
            url = 'https://bitbucket.org/imcovangent/cmdows/raw/master/schema/' + version + '/cmdows.xsd'
            schema_string = urllib2.urlopen(url).read()
        except (urllib2.URLError, OSError):
            logger.info('Could not reach the CMDOWS schema file online. A local copy is used.')
            versions = os.listdir(os.path.join(os.path.dirname(__file__), 'schemas'))
            if version in versions:
                schema_string = open(os.path.join(os.path.dirname(__file__), 'schemas/' + version + '/cmdows.xsd'),
                                     'r').read()
            else:
                raise IOError('The specified CMDOWS schema version could not be found. '
                              'Are you sure that version ' + version + ' is an official CMDOWS schema version?')
        schema = etree.XMLSchema(etree.XML(schema_string))
        return schema

    def simplify(self):
        """Method to simplify everything"""
        for name in dir(self):
            if name.startswith('simplify_'):
                method = getattr(self, name)
                method()

    def simplify_equations(self):
        """Method to replace duplicate equations elements by a single equations element and refs to this element"""
        # Make deepcopy of all equations (as some attributes are going to be deleted for the check)
        equations_xml = copy.deepcopy(self.root.xpath('.//equations'))
        # Create dictionary with all equations
        equations_dict = {}
        for equation in equations_xml:
            id = equation.attrib['uID']
            del equation.attrib['uID']
            equations_dict[id] = etree.tostring(equation)
        # Create reverse dictionary with all equations
        equations_dict_rev = {}
        for key, value in equations_dict.items():
            equations_dict_rev.setdefault(value, set()).add(key)
        # Find duplicates
        equations_duplicates = [values for key, values in equations_dict_rev.items() if len(values) > 1]
        # For every duplicate keep only the first equations element and replace other equations elements by a ref
        for equations_duplicate in equations_duplicates:
            for id in list(equations_duplicate)[1:]:
                old_equations_element = self.root.xpath('.//equations[@uID="' + id + '"]')[0]
                new_equations_element = etree.Element('equationsUID')
                new_equations_element.text = list(equations_duplicate)[0]
                old_equations_element.getparent().replace(old_equations_element, new_equations_element)

    def check(self):
        """Method to execute all checks"""
        result = True
        for name in dir(self):
            if name.startswith('check_'):
                method = getattr(self, name)
                result = result and method()
        return result

    def check_schema(self):
        """Method to check if a CMDOWS file adheres to its schema"""
        try:
            result = self.schema().validate(self.root)
        except:
            result = False
        if not result:
            logger.warning('The CMDOWS file does not adhere to its schema.')
        return result

    def check_uids(self):
        """Method to check if all uIDs are actually unique in a CMDOWS file"""
        ids = [element.attrib['uID'] for element in self.root.xpath('.//*[@uID]')]
        result = (len(ids) == len(set(ids)))
        if not result:
            duplicates = [k for k, v in Counter(ids).items() if v > 1]
            logger.warning('The following uIDs are not unique: ' + ', '.join(duplicates))
        return result

    def check_references(self):
        """Method to check if references are actually pointing to a uID in a CMDOWS file"""
        ids = [element.attrib['uID'] for element in self.root.xpath('.//*[@uID]')]
        references = [element.text for element in self.root.xpath('.//*[contains(name(), "UID")]')]
        invalids = list(set([reference for reference in references if reference not in ids]))
        result = (len(invalids) == 0)
        if not result:
            logger.warning('The following uIDs do not exist although they are referred to: ' + ', '.join(invalids))
        return result

    def assert_element_tag(self, el, expected_tag):
        """Method to assert that the tag of an element is as expected."""
        if expected_tag:
            assert el.tag == expected_tag, 'Element should have tag {}, but has tag: {}.'.format(expected_tag, el.tag)

    # ----------------------------------------- #
    #             Get functions                 #
    # ----------------------------------------- #
    def get_inputs_uids(self, exblock_uid):
        """Method to collect the inputs of a CMDOWS file executableBlock entry"""
        assert self.get_element_of_uid(exblock_uid).getparent().getparent().tag == 'executableBlocks', \
            'UID ' + exblock_uid + ' does not seem to refer to an executableBlock.'
        xpath = self.get_xpath_of_uid(exblock_uid)
        return self.root.xpath(xpath + '/inputs/input/parameterUID/text()')

    def get_outputs_uids(self, exblock_uid):
        """Method to collect the outputs of a CMDOWS file executableBlock entry"""
        assert self.get_element_of_uid(exblock_uid).getparent().getparent().tag == 'executableBlocks', \
            'UID ' + exblock_uid + ' does not seem to refer to an executableBlock.'
        xpath = self.get_xpath_of_uid(exblock_uid)
        return self.root.xpath(xpath + '/outputs/output/parameterUID/text()')

    def get_element_of_uid(self, uid, expected_tag=None):
        """Method to get the element based on a UID value."""
        xpath_expression = get_uid_search_xpath(uid)
        els = self.root.xpath(xpath_expression)
        if len(els) > 1:
            raise AssertionError('Multiple elements with UID ' + uid + ' found. Use "check_uids()" to check if all UIDs'
                                                                       ' are unique.')
        elif len(els) == 0:
            raise AssertionError('Could not find element with UID ' + uid + '.')
        self.assert_element_tag(els[0], expected_tag)
        return els[0]

    def get_xpath_of_uid(self, uid, expected_tag=None):
        """Method to get the xpath based on a UID value."""
        el = self.get_element_of_uid(uid, expected_tag=None)
        return el.getroottree().getpath(el)

    def get_executable_blocks_uids(self):
        """Method to get a list of all the executable block UIDs present in the file."""
        uid_list = []
        # First collect the executable blocks from the main element
        el = self.root.xpath('/cmdows/executableBlocks')
        assert len(el) == 1, '"/cmdows/executableBlocks" is not a unique XPath. Check given CMDOWS file structure.'
        for exblock_types in el[0].iterchildren():
            for blocks in exblock_types.iterchildren():
                try:
                    uid_list.append(blocks.attrib['uID'])
                except:
                    raise AttributeError('Could not find the uID attribute for this element: {}.'.format(blocks))
        # Then collect the executable blocks from the architecture elements
        el = self.root.xpath('/cmdows/architectureElements/executableBlocks')
        if el:
            assert len(el) == 1, '"/cmdows/architectureElements/executableBlocks" is not a unique XPath. ' \
                                 'Check given CMDOWS file structure.'
            for arblock_type in el[0].iterchildren():
                for arblock in arblock_type.iterchildren():
                    try:
                        uid_list.append(arblock.attrib['uID'])
                    except:
                        if arblock_type.tag in ['coordinators', 'optimizers', 'convergers', 'consistencyConstraintFunctions']:
                            raise AttributeError('Could not find the uID attribute for this element: {}.'.format(arblock))
        return uid_list

    def get_parameters_uids(self):
        """Method to get a list of all the parameter UIDs present in the file."""
        uid_list = []
        # First collect the parameters from the main element
        el = self.root.xpath('/cmdows/parameters')
        assert len(el) == 1, '"/cmdows/parameters" is not a unique XPath. Check given CMDOWS file structure.'
        for param in el[0].iterchildren():
            try:
                uid_list.append(param.attrib['uID'])
            except:
                raise AttributeError('Could not find the uID attribute for this element: {}.'.format(param))
        # Then collect the parameters from the architecture elements
        el = self.root.xpath('/cmdows/architectureElements/parameters')
        if el:
            assert len(el) == 1, '"/cmdows/architectureElements/parameters" is not a unique XPath. ' \
                                 'Check given CMDOWS file structure.'
            for param_type in el[0].iterchildren():
                for param in param_type.iterchildren():
                    try:
                        uid_list.append(param.attrib['uID'])
                    except:
                        raise AttributeError('Could not find the uID attribute for this element: {}.'.format(param))
        return uid_list

    def get_design_competences_uids(self):
        """Method to get a list of all the design competences UIDs present in the file."""
        uid_list = []
        el = self.root.xpath('/cmdows/executableBlocks/designCompetences')
        assert len(el) <= 1, '"/cmdows/executableBlocks/designCompetences" is not a unique XPath. ' \
                             'Check given CMDOWS file structure.'
        if len(el) == 1:
            for dc in el[0].iterchildren():
                try:
                    uid_list.append(dc.attrib['uID'])
                except:
                    raise AttributeError('Could not find the uID attribute for this DC element: {}.'.format(dc))
        return uid_list

    def get_mathematical_functions_uids(self):
        """Method to get a list of all the mathematical functions UIDs present in the file."""
        uid_list = []
        el = self.root.xpath('/cmdows/executableBlocks/mathematicalFunctions')
        assert len(el) <= 1, '"/cmdows/executableBlocks/mathematicalFunctions" is not a unique XPath. ' \
                             'Check given CMDOWS file structure.'
        if len(el) == 1:
            for mf in el[0].iterchildren():
                try:
                    uid_list.append(mf.attrib['uID'])
                except:
                    raise AttributeError('Could not find the uID attribute for this MF element: {}.'.format(mf))
        return uid_list

    def get_used_parameter_uids(self):
        """Method to get a list of all the parameter UIDs used in the file."""
        uid_list = []
        el = self.root.xpath('/cmdows/executableBlocks/mathematicalFunctions')
        assert len(el) <= 1, '"/cmdows/executableBlocks/mathematicalFunctions" is not a unique XPath. ' \
                             'Check given CMDOWS file structure.'
        if len(el) == 1:
            for mf in el[0].iterchildren():
                try:
                    uid_list.append(mf.attrib['uID'])
                except:
                    raise AttributeError('Could not find the uID attribute for this MF element: {}.'.format(mf))
        return uid_list

    # ----------------------------------------- #
    #       Add / change file functions         #
    # ----------------------------------------- #
    def add_header(self, creator, description, timestamp=None, fileVersion="0.0", cmdowsVersion="0.7"):
        """Method to add a header to a CMDOWS file."""

        # Assert header element exists
        el = self.ensure_abs_xpath('/cmdows/header')

        # Add elements
        el.add("creator", creator)
        el.add("description", description)
        el.add("timestamp", str(datetime.now()) if timestamp is None else timestamp)
        el.add("fileVersion", fileVersion)
        el.add("cmdowsVersion", cmdowsVersion)
        return

    def add_contact(self, name, email, uid, company=None, department=None, function=None, address=None, telephone=None, country=None, roles=None):
        """Method to add a contact element to the organization branch."""

        # Assert that there is a path to the contacts element or add one
        parent_element = self.ensure_abs_xpath('/cmdows/header/organization/contacts')

        # Assert that there is no existing element with the uid
        try:
            self.get_element_of_uid(uid)
            raise AssertionError('UID {} is already used in the CMDOWS file at {}'.format(uid, self.get_xpath_of_uid(uid)))
        except:
            pass

        # Add the contact details
        contact_element = Element('contact', uID=uid)
        contact_element.add('name', name)
        contact_element.add('email', email)
        contact_element.add('company', company, only_add_if_valued=True)
        contact_element.add('department', department, only_add_if_valued=True)
        contact_element.add('function', function, only_add_if_valued=True)
        contact_element.add('address', address, only_add_if_valued=True)
        contact_element.add('telephone', telephone, only_add_if_valued=True)
        contact_element.add('country', country, only_add_if_valued=True)

        parent_element.append(contact_element)

        if roles:
            if isinstance(roles, list):
                [self.add_actor(uid, role) for role in roles]
            elif isinstance(roles, basestring):
                self.add_actor(uid, roles)
            else:
                raise IOError('Invalid type for roles provided: {}.'.format(type(roles)))
        return

    def add_dc(self, uid, id, mode_id, instance_id, version, label):
        """Method to add a designCompetence element to the designCompetences branch."""

        # Assert that there is a path to the designCompetences element or add one
        parent_element = self.ensure_abs_xpath('/cmdows/executableBlocks/designCompetences')

        # Assert that there is no existing element with the uid
        try:
            self.get_element_of_uid(uid)
            raise AssertionError(
                'UID {} is already used in the CMDOWS file at {}'.format(uid, self.get_xpath_of_uid(uid)))
        except:
            pass

        # Add the design competence details
        dc_element = Element('designCompetence', uID=uid)
        dc_element.add('ID', id)
        dc_element.add('modeID', mode_id)
        dc_element.add('instanceID', instance_id)
        dc_element.add('version', version)
        dc_element.add('label', label)

        parent_element.append(dc_element)

        return

    def add_element_to_element_of_uid(self, uid, element_to_add, expected_tag_uid_el=None, expected_tag_new_el=None):
        """Generic method to add a subelement to an element with a certain UID."""

        # Assert that there is a UID element
        xpath = self.get_xpath_of_uid(uid, expected_tag=expected_tag_uid_el)

        # Assert that an inputs element is given
        if expected_tag_new_el:
            self.assert_element_tag(element_to_add, expected_tag_new_el)

        # Get element of uid
        parent_element = self.get_element_of_uid(uid)

        # Add new element
        parent_element.append(element_to_add)
        return

    def add_dc_inputs_element(self, dc_uid, inputs_element):
        """Method to add a inputs element to a DC element."""
        self.add_element_to_element_of_uid(dc_uid, inputs_element, 'designCompetence', 'inputs')
        return

    def add_dc_outputs_element(self, dc_uid, outputs_element):
        """Method to add a outputs element to a DC element."""
        self.add_element_to_element_of_uid(dc_uid, outputs_element, 'designCompetence', 'outputs')
        return

    def add_dc_general_info(self, dc_uid, description, status=None, creation_date=None, owner_uid=None, creator_uid=None,
                            operator_uid=None, model_definition=None):
        """Method to add a general info element to a dc branch."""

        # Assert that there is a DC element
        xpath = self.get_xpath_of_uid(dc_uid, expected_tag='designCompetence')

        # Assert that the contact_uids exist
        self.get_element_of_uid(owner_uid) if owner_uid else None
        self.get_element_of_uid(creator_uid) if creator_uid else None
        self.get_element_of_uid(operator_uid) if operator_uid else None

        # Assert that the model definition is a dict with the right elements
        if model_definition:
            assert_dict_keys(model_definition, self.MODEL_DEFINITION_ELEMENTS, all_keys_required=False)
            model_definition = dict_to_ord_dict(model_definition, self.MODEL_DEFINITION_ELEMENTS)

        # Assert that there is no existing general info element or else remove it
        self.remove_element_based_on_xpath(xpath + '/metadata/generalInfo')

        # Ensure element to metadata parent
        parent_element = self.ensure_abs_xpath(xpath + '/metadata')

        # Add the contact details
        general_info_element = Element('generalInfo')
        general_info_element.add('description', description)
        general_info_element.add('status', status, only_add_if_valued=True)
        general_info_element.add('creation_date', creation_date, only_add_if_valued=True, camel_case_conversion=True)
        general_info_element.add('owner', {'contactUID': owner_uid}) if owner_uid else None
        general_info_element.add('creator', {'contactUID': creator_uid}, only_add_if_valued=True) if creator_uid else None
        general_info_element.add('operator', {'contactUID': operator_uid}, only_add_if_valued=True) if operator_uid else None
        general_info_element.add('model_definition', model_definition, camel_case_conversion=True,
                                 only_add_if_valued=True)
        parent_element.append(general_info_element)
        return

    def add_dc_performance_info(self, dc_uid, precision=None, fidelity_level=None, run_time=None, verification=None):
        """Method to add a performance info element to a DC branch."""

        # Assert that there is a DC element
        xpath = self.get_xpath_of_uid(dc_uid, expected_tag='designCompetence')

        # Assert that there is at least one element with a value
        assert sum(x is not None for x in [precision, fidelity_level, run_time, verification]) > 0, \
            'At least one element must have a value.'

        # Assert that the verification is a dict with the right elements
        if verification:
            assert_dict_keys(verification, self.VERIFICATION_ELEMENTS, all_keys_required=True)
            # Assert the verifier is a contact
            self.get_element_of_uid(verification['verifier'])

        # Assert that there is no existing general info element or else remove it
        self.remove_element_based_on_xpath(xpath + '/metadata/performanceInfo')

        # Ensure elements to metadata parent
        parent_element = self.ensure_abs_xpath(xpath + '/metadata')

        # Add the contact details
        performance_info_element = Element('performanceInfo')
        performance_info_element.add('precision', precision, only_add_if_valued=True)
        performance_info_element.add('fidelityLevel', fidelity_level, only_add_if_valued=True)
        performance_info_element.add('run_time', run_time, only_add_if_valued=True, camel_case_conversion=True)
        parent_element.append(performance_info_element)

        if verification:
            self.add_dc_verification(dc_uid, verification['method'], verification['verifier'], verification['result'],
                                     verification['date'], verification['version'])
        return

    def add_dc_verification(self, dc_uid, method, verifier, result, date, version):
        """Method to add a verification to a DC"""

        # Assert that there is a DC element
        xpath = self.get_xpath_of_uid(dc_uid, expected_tag='designCompetence')

        # Assert that the verifier is a contact
        self.get_element_of_uid(verifier, expected_tag='contact') if verifier else None

        # Ensure elements to verifications parent
        parent_element = self.ensure_abs_xpath(xpath + '/metadata/performanceInfo/verifications')

        # Find verifications element
        verification_element = Element('verification')
        verification_element.add('method', method)
        verification_element.add('verifier', {'contactUID' : verifier}, camel_case_conversion=False)
        verification_element.add('result', result)
        verification_element.add('date', date)
        verification_element.add('version', version)

        parent_element.append(verification_element)
        return

    def add_dc_remote_component_info(self, dc_uid, single_or_multi_execution, job_name, remote_engineer,
                                     notification_message, data_exchange_dict=None):
        """Method to add a remote execution info element to a dc branch."""

        # Assert that there is a DC element
        xpath = self.get_xpath_of_uid(dc_uid, expected_tag='designCompetence')

        # Assert the single/multi input
        assert single_or_multi_execution in self.SINGLE_MULTI_OPTIONS, 'single_or_multi_execution should be either {}, now is {}'.format(self.SINGLE_MULTI_OPTIONS, single_or_multi_execution)

        # Assert the remote_engineer is a contact
        self.get_element_of_uid(remote_engineer, expected_tag='contact')

        if data_exchange_dict:
            assert_dict_keys(data_exchange_dict, self.DATA_EXCHANGE_SETTINGS_ELEMENTS)
            data_exchange_dict = dict_to_ord_dict(data_exchange_dict, self.DATA_EXCHANGE_SETTINGS_ELEMENTS)

        # Assert that there is an execution info element and remove a potential existing remoteComponent element
        parent_element = self.ensure_abs_xpath(xpath + '/metadata/executionInfo')
        self.remove_element_based_on_xpath(xpath + '/metadata/executionInfo/remoteComponentInfo')

        # Add the remote component element
        remote_component_element = Element('remoteComponentInfo')
        remote_component_element.add('job_settings',
                                     value=OrderedDict((('single_or_multi_execution',single_or_multi_execution),
                                                       ('job_name', job_name),
                                                       ('remote_engineer', {'contact_UID' : remote_engineer}),
                                                       ('notification_message', notification_message))),
                                     camel_case_conversion=True)
        remote_component_element.add('data_exchange_settings', value=data_exchange_dict, only_add_if_valued=True,
                                     camel_case_conversion=True)
        parent_element.append(remote_component_element)
        return

    def add_new_parameters_from_element(self, parameters_element):
        """Method to add the new parameters based on a parameters element."""

        # First ensure a parameters XPath
        el = self.ensure_abs_xpath('/cmdows/parameters')

        # Determine the list of existing parameters
        existing_parameters = []
        for child in el.iterchildren():
            assert child.attrib['uID'], 'Attribute uID is missing for parameter element.'
            existing_parameters.append(child.attrib['uID'])

        # For each element in the parameters_element determine whether it's new, and then add it (or not)
        for new_child in parameters_element.iterchildren():
            assert new_child.attrib['uID'], 'Attribute uID is missing for new parameter element.'
            new_child_uid = new_child.attrib['uID']
            if new_child_uid not in existing_parameters:
                el.append(new_child)
        return

    def add_actor(self, contact_uid, role):
        """Method to add a role element to the organization branch."""

        # Input assertions
        self.get_element_of_uid(contact_uid)
        assert isinstance(role, basestring), 'Role should be of type string.'
        assert role in self.ROLES_OPTIONS, 'Role {} does not exist.'.format(role)

        # Assert that there is a path to the roles element or add one
        target_element = make_camel_case(role, make_plural_option=True)
        parent_element = self.ensure_abs_xpath('/cmdows/header/organization/organigram/' + target_element)

        # Add the role
        parent_element.add(role, OrderedDict((('contact_uid', contact_uid),)), camel_case_conversion=True)

        return

    def add_subelement(self, element, subelement_xpath_tag):
        if "@uID" in subelement_xpath_tag:
            el_tag = find_until(subelement_xpath_tag, '[')
            uid_attr = find_between(subelement_xpath_tag, '[@uID="', '"]')
            element.append(Element(el_tag, uID=uid_attr))
        elif "[" in subelement_xpath_tag:
            el_tag = find_until(subelement_xpath_tag, '[')
            element.append(Element(el_tag))
        else:
            element.append(Element(subelement_xpath_tag))
        return

    def ensure_abs_xpath(self, xpath):
        """Method to ensure that the elements given by an absolute XPath exist."""
        split_path = xpath.split('/')
        assert not split_path[0] and split_path[-1] and len(split_path) > 1, \
            'Invalid XPath ({}) provided. XPath should start with / sign and have at least one entry.'.format(xpath)
        for idx, eltag in enumerate(split_path[1:]):
            local_xpath = '/'.join(split_path[0:idx + 2])
            el = self.root.xpath(local_xpath)
            assert len(el) <= 1, 'Non-unique XPath {} provided.'.format(local_xpath)
            if not el:
                previous_xpath = '/'.join(split_path[0:idx + 1])
                el_pr = self.root.xpath(previous_xpath)
                self.add_subelement(el_pr[0], eltag)
        return self.root.xpath(local_xpath)[0]

    def resolve_uids(self):
        """Method to rename duplicate UIDs in a CMDOWS file"""
        logger.warning('The resolve_uids method is a hack and should not be used.')
        ids = [element.attrib['uID'] for element in self.root.xpath('.//*[@uID]')]
        result = (len(ids) == len(set(ids)))
        if not result:
            duplicates = [k for k, v in Counter(ids).items() if v > 1]
            for duplicate in duplicates:
                duplicate_elements = self.root.xpath('.//*[@uID="' + duplicate + '"]')
                for duplicate_id, duplicate_element in enumerate(duplicate_elements):
                    duplicate_element.attrib['uID'] = duplicate_element.attrib['uID'] + '_' + str(duplicate_id)

    # ----------------------------------------- #
    #             Remove functions              #
    # ----------------------------------------- #
    def remove_inputs(self, exblock_uid):
        """Method to remove the inputs of a CMDOWS file executableBlock entry"""
        assert self.get_element_of_uid(exblock_uid).getparent().getparent().tag == 'executableBlocks', \
            'UID ' + exblock_uid + ' does not seem to refer to an executableBlock.'
        self.remove_children_of_xpath(exblock_uid, children_to_remove=['inputs'])

    def remove_outputs(self, exblock_uid):
        """Method to remove the outputs of a CMDOWS file executableBlock entry"""
        assert self.get_element_of_uid(exblock_uid).getparent().getparent().tag == 'executableBlocks', \
            'UID ' + exblock_uid + ' does not seem to refer to an executableBlock.'
        self.remove_children_of_xpath(exblock_uid, children_to_remove=['outputs'])

    def remove_in_and_outputs(self, exblock_uid):
        """Method to remove the in- and outputs of a CMDOWS file executableBlock entry"""
        assert self.get_element_of_uid(exblock_uid).getparent().getparent().tag == 'executableBlocks', \
            'UID ' + exblock_uid + ' does not seem to refer to an executableBlock.'
        self.remove_children_of_xpath(exblock_uid, children_to_remove=['inputs', 'outputs'])

    def remove_children_of_uid(self, uid, children_to_remove='__all__', children_to_keep='__none__'):
        """Method to remove the children of a CMDOWS file element based on a UID."""
        el = self.get_element_of_uid(uid)
        for child in el.iterchildren():
            if children_to_remove == '__all__':
                if not child.tag in children_to_keep:
                    el.remove(child)
            elif child.tag in children_to_remove:
                if child.tag in children_to_keep:
                    raise AssertionError("Child tag {} is both in the children_to_remove and _keep list"
                                         .format(child.tag))
                el.remove(child)

    def remove_children_of_xpath(self, xpath, children_to_remove='__all__', children_to_keep='__none__'):
        """Method to remove the children of a CMDOWS file element based on an XPath."""
        el = self.root.xpath(xpath)
        for child in el.iterchildren():
            if children_to_remove == '__all__':
                if not child.tag in children_to_keep:
                    el.remove(child)
            elif child.tag in children_to_remove:
                if child.tag in children_to_keep:
                    raise AssertionError("Child tag {} is both in the children_to_remove and _keep list"
                                         .format(child.tag))
                el.remove(child)

    def remove_parameters_element(self):
        """Method to remove a parameters element from a CMDOWS file."""
        el = self.root.xpath('/cmdows/parameters')
        assert len(el) <= 1, '"/cmdows/parameters" is not a unique XPath. Check given CMDOWS file structure.'
        if el:
            el[0].getparent().remove(el[0])

    def remove_workflow_element(self):
        """Method to remove a workflow element from a CMDOWS file."""
        el = self.root.xpath('/cmdows/workflow')
        assert len(el) <= 1, '"/cmdows/workflow" is not a unique XPath. Check given CMDOWS file structure.'
        if el:
            el[0].getparent().remove(el[0])

    def remove_data_graph_element(self):
        """Method to remove a dataGraph element from a CMDOWS file."""
        el = self.root.xpath('/cmdows/workflow/dataGraph')
        assert len(el) <= 1, '"/cmdows/workflow/dataGraph" is not a unique XPath. Check given CMDOWS file structure.'
        if el:
            el[0].getparent().remove(el[0])

    def remove_process_graph_element(self):
        """Method to remove a processGraph element from a CMDOWS file."""
        el = self.root.xpath('/cmdows/workflow/processGraph')
        assert len(el) <= 1, '"/cmdows/workflow/processGraph" is not a unique XPath. Check given CMDOWS file structure.'
        if el:
            el[0].getparent().remove(el[0])

    def remove_element_based_on_uid(self, uid, expected_tag=None):
        """Method to remove an element based on its UID."""
        el = self.get_element_of_uid(uid)
        self.assert_element_tag(el, expected_tag)
        el.getparent().remove(el)

    def remove_element_based_on_xpath(self, xpath, expected_amount=None, expected_text=None, higher_level_removal=None):
        """Method to remove an element based on its XPath."""
        els = self.root.xpath(xpath)
        if expected_amount:
            assert len(els) == expected_amount, '{} element(s) expected, found {}.'.format(expected_amount, len(els))
        for el in els:
            remove = True if (el.text == expected_text or expected_text is None) else False
            if remove:
                el_upper = el.getparent()
                if higher_level_removal:
                    for i in [0]*higher_level_removal:
                        el = el_upper
                        el_upper = el.getparent()
                el_upper.remove(el)

    def remove_contact(self, contact_uid):
        """Method to remove a contact based on its UID."""
        self.remove_element_based_on_uid(contact_uid, expected_tag='contact')

    def remove_parameter(self, param_uid):
        """Method to remove a parameter based on its UID."""
        self.remove_element_based_on_uid(param_uid, expected_tag='parameter')

    def remove_parameters(self, params_uids):
        """Method to remove a list of parameters based on their UID."""
        for param_uid in params_uids:
            self.remove_element_based_on_uid(param_uid, expected_tag='parameter')

    def remove_actor(self, role, uid):
        # Input assertions
        assert isinstance(role, basestring), 'Role should be of type string.'
        assert role in ['architect', 'integrator', 'collaborativeEngineer', 'toolSpecialist',
                        'customer'], 'Role {} does not exist.'.format(role)
        # Remove actor if found
        self.remove_element_based_on_xpath('/cmdows/header/organization/organigram/' + role + 's/' + role + '/contactUID', expected_text=uid, higher_level_removal=1)

        # Remove parent element if empty
        els = self.root.xpath('/cmdows/header/organization/organigram/' + role + 's/' + role)
        if not els:
            self.remove_element_based_on_xpath('/cmdows/header/organization/organigram/' + role + 's', expected_amount=1)

    # ----------------------------------------- #
    #             Export functions              #
    # ----------------------------------------- #
    def save(self, file_path=None, pretty_print=False, method='xml', xml_declaration=True, encoding='UTF-8'):
        """Method to save a manipulated CMDOWS file"""
        if file_path:
            file_path = file_path
        elif self.file:
            file_path = self.file
        else:
            raise IOError('Please specify the path for the CMDOWS file.')
        ElementTree(self.root).write(file_path, pretty_print=pretty_print, method=method,
                                     xml_declaration=xml_declaration, encoding=encoding)

# Set element on the module level
parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=ExtendedElement))
Element = parser.makeelement
