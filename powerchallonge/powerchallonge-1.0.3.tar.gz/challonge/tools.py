import requests
import json
import xml.etree.ElementTree as ET

API_ENDPOINT = 'https://api.challonge.com/v1/tournaments'
user_settings = {}
user_settings['configured'] = False
allowed_easy_tournament_identifier = [False, True]
allowed_query_type = ['.json', '.xml']
allowed_raw_response = [False, True]
allowed_verbose_level = [0, 1, 2]
allowed_test_mode = [True, False]


class UserSettingsError(UserWarning):
    '''
    This error will be raised if the settings configured
    are incorrect or missing.
    '''
    pass


class ChallongeApiError(UserWarning):
    '''
    This error will be raised if HTTP Response code != 200
    '''
    pass


def set_user_settings(api_key):
    '''Set the user settings to be used later on'''
    user_settings['api_key'] = api_key
    user_settings[
        'easy_tournament_identifier'] = allowed_easy_tournament_identifier[0]
    user_settings['query_type'] = allowed_query_type[0]
    user_settings['raw_response'] = allowed_raw_response[0]
    user_settings['verbose_level'] = allowed_verbose_level[0]
    user_settings['test_mode'] = allowed_test_mode[0]
    user_settings['configured'] = True


def set_user_settings_advanced(api_key, easy_tournament_identifier, query_type,
                               raw_response, verbose_level, test_mode):
    '''Set the user settings to be used later on'''

    user_settings['api_key'] = api_key

    if easy_tournament_identifier in allowed_easy_tournament_identifier:
        user_settings[
            'easy_tournament_identifier'] = easy_tournament_identifier
    else:
        raise UserSettingsError(
            'easy_tournament_identifier must be True or False (type bool)')

    if query_type in allowed_query_type:
        user_settings['query_type'] = query_type
    else:
        raise UserSettingsError(
            'query_type must be ".json" or ".xml" (type str)')

    if raw_response in allowed_raw_response:
        user_settings['raw_response'] = raw_response
    else:
        raise UserSettingsError(
            'raw_response must be True or False (type bool)')

    if verbose_level in allowed_verbose_level:
        user_settings['verbose_level'] = verbose_level
    else:
        raise UserSettingsError('verbose_level must be 0, 1 or 2 (type int)')
    if test_mode in allowed_test_mode:
        user_settings['test_mode'] = test_mode
    else:
        raise UserSettingsError(
            'test_mode must be True or False (type bool)')
    user_settings['configured'] = True


def check_if_user_settings_are_configured(user_settings):
    if user_settings['configured'] == False:
        raise UserSettingsError("You must configure your settings using the "
                                'challonge.set_user_settings() '
                                'or challonge.set_user_settings_advanced()'
                                'function before '
                                'using powerchallonge!')


def request(method, target, api_method, dict_prefix, conversion, **params):
    '''API request method'''

    check_if_user_settings_are_configured(user_settings)
    query_type = user_settings['query_type']
    request_url = API_ENDPOINT + target + query_type

    if params:
        params = params['params']
        params = convert_booleans_for_challonge(params)
        if conversion == 1:
            params = convert_params(params, dict_prefix)
            if dict_prefix == "participants[]":
                dict_prefix = "participant"

    if bool(params) == False:
        params = {'api_key': user_settings['api_key']}
    else:
        params['api_key'] = user_settings['api_key']

    if user_settings['verbose_level'] > 1:
        print('Challonge REST API Method : ' + api_method)
        print('Requesting URL : ' + request_url)
    # print(params)
    response = requests.request(method, request_url, params=params)
    if user_settings['raw_response'] == True:
        return response
    else:
        output = convert_object(
            response.text, dict_prefix, query_type, response.status_code)
        response_feedback(response.status_code, output)
        return output


def response_feedback(response_code, output):
    '''Handling the response and printing some feedback'''

    verbose_level = user_settings['verbose_level']

    if user_settings['verbose_level'] > 1:
        if response_code == 200:
            print('Response : HTTP 200 - OK')
    if response_code != 200 and response_code != 500:
        errors = 'Errors : ' + str(output['errors'])
        if response_code == 401:
            if user_settings['test_mode'] == False and verbose_level >= 1:
                print(
                    'Response : HTTP 401 - Unauthorized '
                    '(Invalid API key or insufficient permissions)')
                print(errors)
            elif user_settings['test_mode'] == True:
                raise ChallongeApiError('Response : HTTP 401 - Unauthorized '
                                        '(Invalid API key or insufficient '
                                        'permissions) ' + errors)
        elif response_code == 404:
            if user_settings['test_mode'] == False and verbose_level >= 1:
                print('Response : HTTP 404 - Object not found within your '
                      'account scope')
                print(errors)
            elif user_settings['test_mode'] == True:
                raise ChallongeApiError('Response : HTTP 404 - Object not '
                                        'found within your '
                                        'account scope ' + errors)
        elif response_code == 406:
            if user_settings['test_mode'] == False and verbose_level >= 1:
                print('Response : HTTP 406 - Requested format '
                      'is not supported -'
                      'request JSON or XML only')
                print(errors)
            elif user_settings['test_mode'] == True:
                raise ChallongeApiError('Response : HTTP 406 - '
                                        'Requested format is not supported -'
                                        'request JSON or XML only ' + errors)
        elif response_code == 422:
            if user_settings['test_mode'] == False and verbose_level >= 1:
                print('Response : HTTP 422 - Validation error(s) for '
                      'create or '
                      'update method')
                print(errors)
            elif user_settings['test_mode'] == True:
                raise ChallongeApiError('Response : HTTP 422 - '
                                        'Validation error(s) for '
                                        'create or '
                                        'update method ' + errors)
    if response_code == 500:
        if user_settings['test_mode'] == False and verbose_level >= 1:
            print('Response : HTTP 500 - Something went wrong on '
                  'the challonge end')
        elif user_settings['test_mode'] == True:
            raise ChallongeApiError('Response : HTTP 500 - '
                                    'Something went wrong on '
                                    'the challonge end')
        # Challoonge doesn't output a proper JSON in case of error 500
        # print('Errors : ' + str(output['errors']))


def json_to_params(json_file_path):
    '''
    Convert a .json file to a python dictionnary, only supports single parent
    type json files
    the childs will be the key:elements in the dictionnary
    '''

    json_file = open(json_file_path, 'r')
    dict1 = json.load(json_file)
    prefix = list(dict1.keys())[0]
    dict2 = dict1[prefix]
    json_file.close()
    return dict2


def xml_to_params(xml_file_path):
    '''Convert a .xml file to a python dictionnary
    only supports single parent type xml files
    the childs will be the key:elements in the dictionnary
    '''

    params = {}
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    for child in root:
        if child.attrib:
            if child.attrib['type'] == 'list':
                list1 = child.text.split(",")
                params[child.tag] = list1
        else:
            params[child.tag] = child.text
    return params


def convert_params(params, prefix):
    '''Change prefix of a python dictionnary
    (necessary in some Challonge API methods)
    '''

    new_params = {}
    for key in params:
        new_key = prefix + '[' + key + ']'
        new_params[new_key] = params[key]
    return new_params


def convert_identifier(identifier):
    '''
    Convert a full url to a challonge API like URL, example :
    'https://challonge.com/mycup1' will become 'mycup1'
    'https://myorg.challonge.com/mycup1' will become 'myorg-mycup1'
    '''
    check_if_user_settings_are_configured(user_settings)

    if user_settings['easy_tournament_identifier'] == True:
        if isinstance(identifier, int) == True:
            tournament_id = str(identifier)
            return tournament_id

        challonge_prefix = 'http://challonge.com/'

        if identifier[0:21] == challonge_prefix:
            tournament_url = identifier[21:]
            return tournament_url
        else:
            url = identifier
            char_counter = 7
            subdomain = ''
            for char in url[7:]:
                if char == '.':
                    break
                subdomain = subdomain + char
                char_counter += 1

            tournament_url = url[char_counter + 15:]

            identifier = subdomain + '-' + tournament_url
            return identifier
    else:
        return identifier


def convert_object(object_content, prefix, object_type, response_code):
    '''
    Convert a Python Request object .text to a Python object (dictionnary,list)
    .xml and .json like responses should provide identical python objects
    '''

    if object_type == ".json":
        if response_code == 200:
            output = json.loads(object_content)
            if prefix == 'participant' and "participants" in output:
                prefix = 'participants'
            if prefix == 'match_attachment' and "match_attachments" in output:
                prefix = 'match_attachments'
            if isinstance(output, dict) == True:
                output = output[prefix]
                return output
            elif isinstance(output, list) == True:
                final_list = []
                for elem in output:
                    final_list.append(elem[prefix])
                return final_list
        else:
            output = json.loads(object_content)
            return output

    elif object_type == ".xml":
        if response_code == 200:
            tree = ET.fromstring(object_content)
            if tree.attrib:
                if tree.attrib['type'] == "array":
                    output = []
                    for elem in tree:
                        output2 = {}
                        for child in elem:
                            output2[child.tag] = child.text
                        output.append(output2)
            else:
                output = {}
                for child in tree:
                    output[child.tag] = child.text
            return output
        else:
            output = {}
            error_list = []
            tree = ET.fromstring(object_content)
            for child in tree:
                error_list.append(child.text)
            output = {'errors': error_list}
            return output


def convert_booleans_for_challonge(dictionnary):
    for elem in dictionnary:
        if dictionnary[elem] == True:
            dictionnary[elem] = "true"
        elif dictionnary[elem] == False:
            dictionnary[elem] = "false"
    return dictionnary
