import re


def import_text_element(tixi, dict, parent_path, element):
    assert isinstance(element, basestring)
    dict[element] = tixi.getTextElement(parent_path+'/'+element)
    return dict


def import_double_element(tixi, dict, parent_path, element):
    assert isinstance(element, basestring)
    dict[element] = tixi.getDoubleElement(parent_path+'/'+element)
    return dict


def ensureElementXPath(tixi, element_path):
    element_path_list = element_path.split('/')
    root_element = element_path_list[1]
    for idx, element in enumerate(element_path_list[1:]):
        if idx == 0:
            if not tixi.checkElement('/' + root_element):
                raise IOError('XML file misses root element: ' + root_element)
        else:
            if '[' in element and ']' in element:
                element = re.sub("[\(\[].*?[\)\]]", "", element)
            if not tixi.checkElement("/".join(element_path_list[0:idx+2])):
                tixi.addTextElement("/".join(element_path_list[0:idx + 1]), element, '')

def ensureElementUXPath(tixi, element_uxpath, reference_tixi=None):

    element_uxpath_list = element_uxpath.split('/')
    root_element = element_uxpath_list[1]

    # Open reference XML file to collect attributes from
    previous_element_xpath = None
    for idx, element in enumerate(element_uxpath_list[1:]):
        # Check or add element
        if idx == 0:
            # Define element path
            element_xpath = '/' + root_element
            previous_element_xpath = element_xpath
            # Check if root node matches / exists
            if not tixi.checkElement(element_xpath):
                raise IOError('XML file misses root element: ' + root_element)
            # Check if root node has attributes
            if reference_tixi:
                n_attr = reference_tixi.getNumberOfAttributes(element_xpath)
                if n_attr:
                    element_is_new = True
                else:
                    element_is_new = False
        else:
            # Define element path (potential issue: /cpacs/element[2] TODO: fix potential issue?!
            if '[' in element and ']' in element:
                # Get value between square brackets
                sq_text = re.findall(re.escape('[')+"(.*)"+re.escape(']'),element)[0]
                element = re.sub("[\(\[].*?[\)\]]", "", element)
                if sq_text.isdigit():
                    element_xpath = previous_element_xpath + '/' + element + '[' + sq_text + ']'
                    if tixi.checkElement(element_xpath):
                        element_is_new = False
                        previous_element_xpath = element_xpath
                    else:
                        tixi.addTextElement(previous_element_xpath, element, '')
                        element_is_new = True
                        previous_element_xpath = element_xpath
                else:
                    element_uid = sq_text
                    if tixi.uIDGetXPath(element_uid):
                        element_is_new = False
                        previous_element_xpath = tixi.uIDGetXPath(element_uid)
                    else:
                        tixi.addTextElement(previous_element_xpath, element, '')
                        element_xpath = previous_element_xpath + '/' + element
                        xpath_ind = tixi.xPathEvaluateNodeNumber(element_xpath)
                        element_xpath += '[' + str(xpath_ind) + ']'
                        tixi.addTextAttribute(element_xpath, 'uID', sq_text)
                        element_is_new = True
                        previous_element_xpath = tixi.uIDGetXPath(element_uid)
            elif not '[' in element and not ']' in element:
                element_xpath = previous_element_xpath + '/' + element
                if tixi.checkElement(element_xpath):
                    element_is_new = False
                    previous_element_xpath = element_xpath
                else:
                    tixi.addTextElement(previous_element_xpath, element, '')
                    element_is_new = True
                    previous_element_xpath = element_xpath
            elif '[' in element and not ']' in element:
                raise IOError('Element has "[" but no "]" character.')
            elif not '[' in element and ']' in element:
                raise IOError('Element has "]" but no "[" character.')

        # Also add element attributes based on reference file, if the element is new!
        if reference_tixi and element_is_new:
            element_uxpath = '/'.join(element_uxpath_list[:idx+2])
            element_xpath_ref = get_xpath_from_uxpath(reference_tixi, element_uxpath)
            assert element_xpath_ref is not None, 'No XPath found for UXPath: %s' % element_uxpath
            element_xpath = get_xpath_from_uxpath(tixi, '/'.join(element_uxpath_list[:idx+2]))
            assert element_xpath is not None, 'No XPath found for UXPath: %s' % element_uxpath
            n_attr = reference_tixi.getNumberOfAttributes(element_xpath_ref)
            for j in range(n_attr):
                # How about duplicate attributes?
                attr_name = reference_tixi.getAttributeName(element_xpath_ref, j+1)
                attr_value = reference_tixi.getTextAttribute(element_xpath_ref, attr_name)
                if not tixi.checkAttribute(element_xpath, attr_name):
                    tixi.addTextAttribute(element_xpath, attr_name, attr_value)
    return previous_element_xpath

def addOrUpdateTextElement(tixi, path, element, value, ensureXPath=False):
    assert isinstance(value, basestring) or value is None
    if not value:
        value = 'None'
    if not ensureXPath:
        tixi.checkElement(path)
    else:
        ensureElementXPath(tixi, path)
    element_path = path + '/' + element
    if tixi.checkElement(element_path):
        tixi.updateTextElement(element_path, value)
    else:
        tixi.addTextElement(path, element, value)


def addOrUpdateDoubleElement(tixi, path, element, value, format='%.6f', ensureXPath=False):
    assert isinstance(value, float)
    if not ensureXPath:
        tixi.checkElement(path)
    else:
        ensureElementXPath(tixi, path)
    element_path = path + '/' + element
    if tixi.checkElement(element_path):
        tixi.updateDoubleElement(element_path, value, format)
    else:
        tixi.addDoubleElement(path, element, value, format)


def addOrUpdateIntegerElement(tixi, path, element, value, format='%d', ensureXPath=False):
    assert isinstance(value, int)
    if not ensureXPath:
        tixi.checkElement(path)
    else:
        ensureElementXPath(tixi, path)
    element_path = path + '/' + element
    if tixi.checkElement(element_path):
        tixi.updateIntegerElement(element_path, value, format)
    else:
        tixi.addIntegerElement(path, element, value, format)



def findXPathWithSearchCriterion(tixi, parent_path, search_element, search_criterion, actual_element):
    search_element_path = parent_path + '/' + search_element
    n_xpaths = tixi.xPathEvaluateNodeNumber(search_element_path)
    assert n_xpaths > 0
    final_xpath = None
    for i in range(n_xpaths):
        xpath = tixi.xPathExpressionGetXPath(search_element_path, i + 1)
        element_value = tixi.getTextElement(xpath)
        if element_value == search_criterion:
            split_xpath = xpath.split("/")[0:-1]
            final_xpath = "/".join(split_xpath)
    if not final_xpath:
        raise IOError('XPath that matches search criteria could not be found.')
    return final_xpath


def addOrAppendFloatVector(tixi, path, element,
                           result_values, format='%.6f',
                           ensureXPath=False):
    assert isinstance(result_values, tuple)
    if not ensureXPath:
        tixi.checkElement(path)
    else:
        ensureElementXPath(tixi, path)
    element_path = path + '/' + element

    if not tixi.checkElement(element_path):
        tixi.addFloatVector(path, element, result_values, 1, format)
    else:
        old_vector_size = tixi.getVectorSize(element_path)
        old_vector = tixi.getFloatVector(element_path, old_vector_size)
        tixi.updateFloatVector(element_path, old_vector + result_values, old_vector_size + 1, format)


def removeElementIfExists(tixi, element_path):
    if tixi.checkElement(element_path):
        tixi.removeElement(element_path)

def get_element_details(tixi, uxpath):
    """
    Function to determine the value and dimension of an xpath element in a reference file.

    :param tixi: TiXi object handle
    :type tixi: TiXi
    :param uxpath: XPath including uIDs
    :type uxpath: basestring
    :return: tuple with element value and dimension
    :rtype: tuple
    """
    # Input assertions
    assert isinstance(uxpath, basestring), 'XPath should be a string.'

    # Determine the element uxpath
    xpath = get_xpath_from_uxpath(tixi, uxpath)


    if xpath:
        try:
            value = tixi.getTextElement(xpath)
            separators = value.count(';')
            if separators == 0:
                dim = 1
            else:
                if value[-1] == ';':
                    dim = separators
                else:
                    dim = separators + 1
        except:
            value = 'XPath "' + xpath + '" could not be found.'
            dim = None
    else:
        value = 'XPath with UXPath "' + uxpath + '" could not be found.'
        dim = None
    return (value, dim)


def get_xpath_from_uxpath(tixi, uxpath):
    """
    Function to determine the XPath belonging to a UXPath.

    :param tixi: tixi handle
    :type tixi: tixi
    :param uxpath: string with full UXPath
    :type uxpath: basestring
    :return: XPath of the UXPath
    :rtype: basestring
    """

    # Determine the element uxpath
    xpath_elements = uxpath.split('/')[1:]
    xpath_elements_rev = xpath_elements[::-1]
    uid = ''

    for idx, el in enumerate(xpath_elements_rev):
        if '[' in el and ']' in el:
            # Determine what's between the brackets
            locator = el[el.find('[') + 1:el.rfind(']')]
            if not locator.isdigit():
                uid = locator
                break

    if len(uid) > 0:
        xpath = tixi.uIDGetXPath(uid)
        if xpath:
            if idx != 0:
                xpath = xpath + '/' + '/'.join(xpath_elements_rev[:idx][::-1])
        else:
            xpath = None
    else:
        xpath = uxpath

    return xpath