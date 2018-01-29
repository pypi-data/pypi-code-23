from datetime import datetime
import re

def parse_jackson(input_json):
    """openBIS uses a library called «jackson» to automatically generate the JSON RPC output.
       Objects that are found the first time are added an attribute «@id».
       Any further findings only carry this reference id.
       This function is used to dereference the output.
    """
    interesting=['tags', 'registrator', 'modifier', 'type', 'parents', 
        'children', 'containers', 'properties', 'experiment', 'sample',
        'project', 'space', 'propertyType', 'entityType', 'propertyType', 'propertyAssignment',
        'externalDms'
    ]
    found = {} 
    def build_cache(graph):
        if isinstance(graph, list):
            for item in graph:
                build_cache(item)
        elif isinstance(graph, dict) and len(graph) > 0:
            for key, value in graph.items():
                if key in interesting:
                    if isinstance(value, dict):
                        if '@id' in value:
                            found[value['@id']] = value
                        build_cache(value)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                if '@id' in item:
                                    found[item['@id']] = item
                                build_cache(item)
                elif isinstance(value, dict):
                    build_cache(value)
                elif isinstance(value, list):
                    build_cache(value)
                    
    def deref_graph(graph):            
        if isinstance(graph, list):
            for i, list_item in enumerate(graph):
                if isinstance(list_item, int):
                    graph[i] = found[list_item]
                else:
                    deref_graph(list_item)
        elif isinstance(graph, dict) and len(graph) > 0:
            for key, value in graph.items():
                if key in interesting:
                    if isinstance(value, dict):
                        deref_graph(value)
                    elif isinstance(value, int):
                        graph[key] = found[value]
                    elif isinstance(value, list):
                        for i, list_item in enumerate(value):
                            if isinstance(list_item, int):
                                if list_item in found:
                                    value[i] = found[list_item]
                                else:
                                    value[i] = list_item
                elif isinstance(value, dict):
                    deref_graph(value)
                elif isinstance(value, list):
                    deref_graph(value)

    build_cache(input_json)
    deref_graph(found)
    deref_graph(input_json)


def check_datatype(type_name, value):
    if type_name == 'INTEGER':
        return isinstance(value, int)
    if type_name == 'BOOLEAN':
        return isinstance(value, bool)
    if type_name == 'VARCHAR':
        return isinstance(value, str)
    return True


def split_identifier(ident):
    bla = []
    bla=ident.upper().split("/")
    results = {}
    try:
        if bla[0] == '':
            bla.pop(0)
        if bla[-1] == '':
            bla.pop(-1)
        results["space"] = bla.pop(0)
        results["code"]  = bla.pop(-1)
        results["experiment"] = bla.pop(0)
    except Exception:
        pass

    return results


def format_timestamp(ts):
    if ts is None:
        return ''
    return datetime.fromtimestamp(round(ts/1000)).strftime('%Y-%m-%d %H:%M:%S')


def is_identifier(ident):
    # assume we got a sample identifier e.g. /TEST/TEST-SAMPLE
    match = re.match('/', ident)
    if match:
        return True
    else:
        return False


def is_permid(ident):
    match = re.match('^\d+\-\d+$', ident)
    if match:
        return True
    else:
        return False


def nvl(val, string=''):
    if val is None:
        return string
    return val
