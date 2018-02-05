import re
import ast
import logging

from collections import OrderedDict

from lxml import etree
from lxml.etree import SubElement

from general import make_camel_case, unmake_camel_case, make_singular


# Settings for the logger
logger = logging.getLogger(__name__)

# Settings for the parser
parser = etree.XMLParser(remove_blank_text=True)


def recursively_stringify(tree):
    """
    Utility function to recursively stringify a ElementTree object (for file comparison).

    :param tree: Input ElementTree object
    :return: List of strings representing the ElementTree object
    """

    string_list = []

    for elem in tree.iter():
        if elem.text is not None and len(elem.text.strip()) > 0:
            string = re.sub('([(\[]).*?([)\]])', '', tree.getpath(elem)) + '/' + elem.text.strip()
            string_list.append(string)
        for attr_name, attr_value in elem.items():
            string = re.sub('([(\[]).*?([)\]])', '', tree.getpath(elem)) + '//' + attr_name + '/' + attr_value
            string_list.append(string)

    string_list.sort()

    return string_list


def recursively_empty(element):
    """
    Utility function to check recursively if a ElementTree object is empty.

    :param element: Input ElementTree object
    :return: Result of the check
    """

    if element.text:
        return False
    return all((recursively_empty(c) for c in element.iterchildren()))


def recursively_unique_attribute(element, attribute='uID'):
    """
    Utility function to check recursively if the values of an attribute of an ElementTree object are unique.

    :param element: Input ElementTree object
    :param attribute: Name of the attribute being checked for uniqueness
    :return: Result of the check
    """

    attribute_list = [e.get(attribute) for e in element.findall('.//*[@' + attribute + ']')]
    attribute_list_unique = list(set(attribute_list))
    result = len(attribute_list) == len(attribute_list_unique)
    if not result:
        duplicate_list = ['"'+attribute+'"' for attribute in attribute_list_unique
                          if attribute_list.count(attribute) > 1]
        logger.warning('There are several attributes with the same uIDs. The (reference) file is not valid. '
                       'The duplicate uIDs are: ' + ', '.join(duplicate_list))
    return result


def get_element_details(tree, xpath):
    """
    Function to determine the value and dimension of an UXPath element in a reference file.

    :param tree: ElementTree object used for finding the XPath
    :param xpath: XPath
    :return: element value and dimension
    """

    # Input assertions
    assert isinstance(xpath, basestring)

    # Search for element value based on XPath
    try:
        values = tree.getroot().xpath(xpath)
        if len(values) > 1:
            logger.warning('The XPath '+xpath+' is not unique in the reference file. Only the first value is used.')
        value = values[0].text
        separators = value.count(';')
        if separators == 0:
            dim = 1
        else:
            if value[-1] == ';':
                dim = separators
            else:
                dim = separators + 1
    except (IndexError, AttributeError):
        # TODO: Shouldn't there rather be a warning and no value?
        value = 'The XPath "' + xpath + '" could not be found in the reference file.'
        dim = None

    return value, dim


def merge(a, b):
    """
    Recursive function to merge a nested tree dictionary (D3.js convention) into a full tree dictionary.

    :param a: full dictionary in which a new element is merged
    :type a: dict
    :param b: element dictionary of the new element
    :type b: dict
    :return: merged dictionary
    :rtype: dict
    """

    if not a:
        a = dict(name=b['name'])

    if 'children' in a and 'children' in b:
        for idx, item in enumerate(a['children']):
            child_exists = False
            if item['name'] == b['children'][0]['name']:
                child_exists = True
                break
        # noinspection PyUnboundLocalVariable
        if not child_exists:
            a['children'].append(b['children'][0])
        else:
            # noinspection PyUnboundLocalVariable
            merge(a['children'][idx], b['children'][0])
    else:
        try:
            a['children'] = b['children']
        except:
            print a
            print b
            raise Exception('A problematic merge has occured. Please check consistency of the graph.')

    return a


def get_uid_search_xpath(uid):
    """ Method to get the XPath expression for a UID which might contain quote characters.

    :param uid: uID string
    :type uid: str
    :return: XPath expression
    :rtype: str
    """
    if '"' in uid or '&quot;' in uid:
        uid_concat = "concat('%s')" % uid.replace('&quot;', "\',\'\"\',\'").replace('"', "\',\'\"\',\'")
        return './/*[@uID=' + uid_concat + ']'
    else:
        return './/*[@uID="' + uid + '"]'


class ExtendedElement(etree.ElementBase):

    def add_process_hierarchy(self, process_hierarchy, mpg):
        """Method to add the hierarchy of the process as metadata to the workflow/processGraph."""

        base_element = self
        # Add loopElements and functionElements for getting the right order
        for idx, element in enumerate(process_hierarchy):
            if isinstance(element, basestring):
                if mpg.node[element]['architecture_role'] in mpg.ARCHITECTURE_ROLES_FUNS[0:4]:
                    if self.find('loopElements') is None:
                        self.add('loopElements')
                    loop_elements = self.find('loopElements')
                    base_element = loop_elements.add('loopElement', relatedUID=element)
                else:
                    if self.find('functionElements') is None:
                        loop_elements = self.add('loopElements') # Added in front to meet schema requirements
                        self.add('functionElements')
                    function_elements = self.find('functionElements')
                    function_elements.add('functionElement', element)
            elif isinstance(element, list):
                base_element.add_process_hierarchy(process_hierarchy[idx], mpg)
            else:
                raise AssertionError('Unexpected element of type {} found for element {}.'.format(type(element),
                                                                                                  element))
        # Remove loopElements if it was not used (was added to make sure schema definition is met if a functionElement
        # is added first.
        if len(self.xpath('//loopElements//loopElement')) == 0:
            if not len(self.xpath('//loopElements')) == 0:
                self.remove(loop_elements)
        return

    def add(self, tag, value=None, attrib=None, camel_case_conversion=False, only_add_if_valued=False, **extra):
        """Method to add a new sub element to the element

        :param tag: The sub element tag
        :type tag: str
        :param value: The sub element value
        :type value: None, str, list, dict, OrderedDict
        :param camel_case_conversion: Option for camel case convention
        :type camel_case_conversion: bool
        :param attrib: An optional dictionary containing sub element attributes
        :param extra: Additional sub element attributes given as keyword arguments
        :return: An element instance
        :rtype: Element
        """
        # Check if value is mandatory for element addition
        if only_add_if_valued and value is None:
            return
        if camel_case_conversion:
            tag = make_camel_case(tag)

        if type(value) == dict or type(value) == OrderedDict:
            child = self._add_dictionary(tag, value, attrib, camel_case_conversion, **extra)

        elif type(value) == list:
            child = self._add_array(tag, value, attrib, camel_case_conversion, **extra)

        else:
            child = self._add_element(tag, value, attrib, **extra)

        return child

    def _add_dictionary(self, tag, dictionary, attrib=None, camel_case_conversion=False, **extra):
        """Method to add a new sub element to the element based on a dictionary

        :param tag: The sub element tag
        :type tag: str
        :param dictionary: The dictionary
        :type dictionary: dict, OrderedDict
        :param camel_case_conversion: Option for camel case convention
        :type camel_case_conversion: bool
        :param attrib: An optional dictionary containing sub element attributes
        :param extra: Additional sub element attributes given as keyword arguments
        :return: An element instance
        :rtype: Element
        """

        child = SubElement(self, tag, attrib, **extra)

        if type(dictionary) == dict:
            iterator = dictionary.iteritems()
        elif type(dictionary) == OrderedDict:
            iterator = dictionary.items()

        # noinspection PyUnboundLocalVariable
        for key, value in iterator:
            if key == 'attrib':
                for attrib_key, attrib_value in value.iteritems():
                    child.set(attrib_key, attrib_value)
            else:
                child.add(key, value, camel_case_conversion=camel_case_conversion)

        return child

    def _add_array(self, tag, array, attrib=None, camel_case_conversion=False, **extra):
        """Method to add a new sub element to the element based on an array

        :param tag: The sub element tag
        :type tag: str
        :param array: The array
        :type array: list
        :param camel_case_conversion: Option for tag conversion from lower_case to camelCase
        :type camel_case_conversion: bool
        :param attrib: An optional dictionary containing sub element attributes
        :param extra: Additional sub element attributes given as keyword arguments
        :return: An element instance
        :rtype: Element
        """

        child = SubElement(self, tag, attrib, **extra)

        for item in array:
            if type(item) == tuple:
                child.add(item[0], item[1], camel_case_conversion=camel_case_conversion)
            else:
                child.add(make_singular(tag), item, camel_case_conversion=camel_case_conversion)

        return child

    def _add_element(self, tag, element, attrib=None, **extra):
        """Method to add a new sub element to the element based on a simple string, float, int, etx.

        :param tag: The sub element tag
        :type tag: str
        :param element: The element
        :type element: str, int, float
        :param attrib: An optional dictionary containing sub element attributes
        :param extra: Additional sub element attributes given as keyword arguments
        :return: An element instance
        :rtype: Element
        """

        child = SubElement(self, tag, attrib, **extra)

        if element is not None:
            try:
                child.text = str(element)
            except UnicodeEncodeError:
                child.text = str(element.encode('ascii', 'replace'))

        return child

    def clean(self):
        """Method to recursively remove empty subelements from the Element"""

        context = etree.iterwalk(self)
        for action, elem in context:
            parent = elem.getparent()
            if recursively_empty(elem):
                parent.remove(elem)

    def findasttext(self, path=None, namespaces=None):
        """Method which extends the findtext method by trying to evaluate the string with the ast module"""

        if path is None:
            element = self
        else:
            element = self.find(path, namespaces)

        value = None

        if element is not None:
            if element.text is not None:
                if element.text.strip():
                    try:
                        value = ast.literal_eval(element.text)
                    except (SyntaxError, ValueError):
                        value = element.text.strip()

        return value

    def finddict(self, path_or_element, namespaces=None, ordered=True, camel_case_conversion=False):
        """Method which reverses the add method and creates a dictionary from an element

        :param path_or_element: (Path to) the element to be analysed
        :type path_or_element: str, Element
        :param namespaces: A prefix-to-namespace mapping that allows the usage of XPath prefixes in path_or_element
        :param ordered: Option for creation of a OrderedDict or a dict respectively
        :type ordered: bool
        :param camel_case_conversion: Option for conversion of the element tags from camelCase to lower_case
        :type camel_case_conversion: bool
        :return: A dictionary
        :rtype: OrderedDict, dict
        """

        # Check if a path or element is provided
        if type(path_or_element) == str:
            elements = self.find(path_or_element, namespaces)
            if elements is None:
                elements = []
        else:
            elements = list(path_or_element)
            if len(elements) == 0:
                elements = [path_or_element]

        # Create dictionary
        if ordered:
            dictionary = OrderedDict()
        else:
            dictionary = dict()

        # Iterate
        if len(elements) == 0:
            return None
        else:
            for element in elements:
                # Values
                if not element.getchildren():
                    value = element.findasttext()
                else:
                    value = element.finddict(element, namespaces, ordered, camel_case_conversion)
                # Attributes
                if len(element.items()) != 0:
                    attrib = {}
                    for item in element.items():
                        attrib.update({item[0]: item[1]})
                    value.update({'attrib': attrib})
                # Keys
                if camel_case_conversion:
                    key = unmake_camel_case(element.tag)
                else:
                    key = element.tag
                # Checks and updates
                if key in dictionary:
                    if type(dictionary[key]) != list:
                        dictionary.update({key: [dictionary[key], value]})
                    else:
                        dictionary[key].append(value)
                else:
                    dictionary.update({key: value})

        # Simplify
        if len(dictionary) == 1:
            dictionary_elem = dictionary.items()[0]
            dictionary = {dictionary_elem[0]: dictionary_elem[1]}
        for key, value in dictionary.iteritems():
            if type(value) == dict:
                if len(value) == 1:
                    subkey = value.keys()[0]
                    if type(dictionary[key][subkey]) == dict:
                        subvalue = [dictionary[key][subkey]]
                    else:
                        subvalue = dictionary[key][subkey]
                    if subkey == make_singular(key):
                        dictionary[key] = subvalue
                    elif type(subvalue) == list:
                        dictionary[key] = [(subkey, elem) for elem in subvalue]

        return dictionary


# Set element on the module level
parser.set_element_class_lookup(etree.ElementDefaultClassLookup(element=ExtendedElement))
Element = parser.makeelement
