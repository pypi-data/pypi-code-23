"""mechanic code generator from an OpenAPI 3.0 specification file.

Usage:
    mechanic build <directory>
    mechanic merge <master> <files>...
    mechanic generate [--models] [--schemas] [--blueprints] [--tests] [--output-docs=<merged-file>] <object_path> <output_file> [--filter-tag=<tag>...] [--exclude-tag=<tag>...] [--schema=<schema_name>...]

Note:
    - 'mechanic generate' is experimental, use with caution

Arguments:
    directory                           Directory that has the mechanicfile

Options:
    -h --help                           Show this screen
    -v --version                        Show version

Examples:
    mechanic build .
"""
# native python
import os
import pkg_resources
import datetime
import json
import copy
import re
from distutils.version import LooseVersion

# third party
import yaml
import yamlordereddictloader
from yamlordereddictloader import OrderedDict
from docopt import docopt

# project
from mechanic.src.compiler import Compiler, Merger, MECHANIC_SUPPORTED_HTTP_METHODS
from mechanic.src.generator import Generator
from mechanic.src.merger import SpecMerger
from mechanic.src.reader import read_mechanicfile


def _render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    import jinja2
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(
        context)


def main():
    with open(pkg_resources.resource_filename(__name__, 'VERSION')) as version_file:
        current_version = version_file.read().strip()

    args = docopt(__doc__, version=current_version)

    if args['build']:
        directory = os.path.expanduser(args['<directory>'])
        filepath = directory + '/mechanic.json'
        try:
            mechanic_options = read_mechanicfile(filepath)
        except FileNotFoundError:
            filepath = directory + '/mechanic.yaml'
            mechanic_options = read_mechanicfile(filepath)
        compiler = Compiler(mechanic_options, mechanic_file_path=filepath)
        compiler.compile()
        Generator(directory, compiler.mech_obj, options=mechanic_options).generate()
    elif args['merge']:
        files_to_merge = args['<files>']
        spec_merger = SpecMerger(files_to_merge, args['<master>'])
        spec_merger.merge()
    elif args['generate']:
        context = {
            'timestamp': datetime.datetime.utcnow(),
            'codeblocks': []
        }
        # if object_path is file, generate all of 'type' (e.g. 'model', 'schema', 'controller')
        if args['<object_path>'].endswith('.yaml') \
                or args['<object_path>'].endswith('.yml') \
                or args['<object_path>'].endswith('.json'):
            # merge oapi file
            oapi_file = args['<object_path>']
            if args['--output-docs']:
                output_docs = args['--output-docs']
                merger = Merger(oapi_file, output_docs)
                merger.merge()
                REMOVE_KEYS = ['x-mechanic-controller', 'x-mechanic-tags', 'x-mechanic-db', 'x-mechanic-schema',
                               'x-mechanic-public', 'x-mechanic-embeddable', 'x-mechanic-model', 'x-mechanic-db-tables']

                m_oapi_obj_copy = copy.deepcopy(merger.oapi_obj)
                SpecMerger.clean_schema_properties(m_oapi_obj_copy)
                for rkey in REMOVE_KEYS:
                    SpecMerger.clean(m_oapi_obj_copy, key=rkey)

                with open(output_docs, "w") as f:
                    if output_docs.endswith(".json"):
                        json_data = json.dumps(m_oapi_obj_copy, indent=3)
                        f.write(json_data)
                    elif output_docs.endswith(".yaml") or output_docs.endswith(".yml"):
                        yaml_data = yaml.dump(OrderedDict(m_oapi_obj_copy),
                                              Dumper=yamlordereddictloader.Dumper,
                                              default_flow_style=False)
                        f.write(yaml_data)
                    else:
                        raise SyntaxError(
                            "Specified output file is not of correct format. Must be either json or yaml.")
            else:
                merger = Merger(oapi_file, 'temp.yaml')
                merger.merge()
                os.remove('temp.yaml')

            oapi_obj = merger.oapi_obj
            oapi_version = oapi_obj.get('info', {}).get('version', '0.0.1')

            filter_tags = args['--filter-tag']
            filter_schema_name = args['--schema']
            exclude_tags = args['--exclude-tag']

            filter_tag_set = set(args['--filter-tag'])
            filter_schema_name_set = set(args['--schema'])
            exclude_tag_set = set(args['--exclude-tag'])

            if args['--models']:
                # first generate any additional tables from components.x-mechanic-db-tables
                for table_name, table_def in oapi_obj['components'].get('x-mechanic-db-tables', {}).items():
                    s2 = set(table_def.get('x-mechanic-tags', []))

                    if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(filter_tags) == 0:
                        context['codeblocks'].append({
                            'type': 'table',
                            'table_name': table_name,
                            'oapi': oapi_obj['components']['x-mechanic-db-tables'][table_name]
                        })

                # next generate models from components.schemas
                for model_name, model in oapi_obj['components']['schemas'].items():
                    if model.get('allOf'):
                        allof_refs = []
                        # first assign 'model' to actual schema data, not the allOf ref
                        for item in model.get('allOf'):
                            if not item.get('$ref'):
                                model = item
                            else:
                                allof_refs.append(item.get('$ref'))

                        for allof_ref in allof_refs:
                            obj, obj_name = merger.follow_reference_link(allof_ref)
                            for prop_name, prop_obj in obj.get('properties').items():
                                if not model['properties'].get(prop_name):
                                    # base property has been overridden in child resource
                                    model['properties'][prop_name] = prop_obj
                                if model.get('required'):
                                    model['required'].extend(obj.get('required', []))

                    # get tags for filtering code generation
                    s2 = set(model.get('x-mechanic-tags', []))

                    if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(filter_tags) == 0:
                        if model.get('x-mechanic-model', {}).get('generate', True):
                            context['codeblocks'].append({
                                'type': 'model',
                                'class_name': model.get('x-mechanic-model', {}).get('class_name', model_name),
                                'base_class_name': model.get('x-mechanic-model', {}).get('base_class', 'db.Model'),
                                'version': model.get('x-mechanic-version', oapi_version),
                                'oapi': model,
                            })
            if args['--schemas']:
                for model_name, model in oapi_obj['components']['schemas'].items():
                    if model.get('allOf'):
                        allof_refs = []
                        # first assign 'model' to actual schema data, not the allOf ref
                        for item in model.get('allOf'):
                            if not item.get('$ref'):
                                model = item
                            else:
                                allof_refs.append(item.get('$ref'))

                        for allof_ref in allof_refs:
                            obj, obj_name = merger.follow_reference_link(allof_ref)
                            for prop_name, prop_obj in obj.get('properties').items():
                                if not model['properties'].get(prop_name):
                                    # base property has been overridden in child resource
                                    model['properties'][prop_name] = prop_obj
                                if model.get('required'):
                                    model['required'].extend(obj.get('required', []))

                    s2 = set(model.get('x-mechanic-tags', []))

                    if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(filter_tags) == 0:
                        if model.get('x-mechanic-schema', {}).get('generate', True):
                            context['codeblocks'].append({
                                'type': 'schema',
                                'class_name': model.get('x-mechanic-schema', {}).get('class_name', model_name + 'Schema'),
                                'base_class_name': model.get('x-mechanic-schema', {}).get('base_class_name', 'ma.ModelSchema'),
                                'version': model.get('x-mechanic-version', oapi_version),
                                'oapi': model,
                            })
            if args['--blueprints']:
                for path_name, path in oapi_obj['paths'].items():
                    # schema = path.get('x-mechanic-controller').get('schema')

                    for method_name, method in path.items():
                        if method_name in MECHANIC_SUPPORTED_HTTP_METHODS:
                            if not oapi_obj['paths'][path_name].get('x-mechanic-controller'):
                                oapi_obj['paths'][path_name]['x-mechanic-controller'] = dict()

                            if not oapi_obj['paths'][path_name]['x-mechanic-controller'].get('methods'):
                                oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'] = dict()

                            if not oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'].get(method_name):
                                oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'][method_name] = dict()

                            # if not oapi_obj['paths'][path_name]['x-mechanic-controller'].get(method_name):
                            #     oapi_obj['paths'][path_name]['x-mechanic-controller'][method_name] = dict()
                            oapi_m = oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'][method_name]
                            oapi_m['many'] = False
                            oapi_m['request_schema'] = None
                            oapi_m['response_schema'] = None
                            oapi_m['operationId'] = method.get('operationId', method_name + '()')
                            oapi_m['parameters'] = []

                            params = method.get('parameters', [])
                            for param in params:
                                if param.get('$ref'):
                                    ref = param.get('$ref')
                                    param_obj, _ = merger.follow_reference_link(ref)

                                    if param_obj and param_obj.get('in') == 'path':
                                        oapi_m['parameters'].append(param_obj.get('name'))
                                else:
                                    if param.get('name'):
                                        oapi_m['parameters'].append(param.get('name'))

                            for response_code, response_obj in method.get('responses', {}).items():
                                if response_code.startswith('2'):
                                    oapi_m['code'] = response_code
                                    resp_schema = response_obj.\
                                        get('content', {}).\
                                        get('application/json', {}).\
                                        get('schema', {})
                                    if resp_schema.get('items') and resp_schema.get('type') == 'array':
                                        oapi_m['many'] = True
                                        ref = resp_schema.get('items', {}).get('$ref')
                                        # ref_obj, _ = merger.follow_reference_link(ref)
                                        schema_name = ref.split('/')[-1]
                                        oapi_m['response_schema'] = schema_name + 'Schema'
                                    else:
                                        if resp_schema.get('$ref'):
                                            ref = resp_schema.get('$ref')
                                            # ref_obj, _ = merger.follow_reference_link(ref)
                                            schema_name = ref.split('/')[-1]
                                            oapi_m['response_schema'] = schema_name + 'Schema'

                            if method.get('requestBody'):
                                req_schema = method.get('requestBody'). \
                                                    get('content', {}). \
                                                    get('application/json', {}). \
                                                    get('schema', {})
                                ref = req_schema.get('$ref')
                                # ref_obj, _ = merger.follow_reference_link(ref)
                                if ref:
                                    schema_name = ref.split('/')[-1]
                                    oapi_m['request_schema'] = schema_name + 'Schema'
                                    oapi_m['parameters'].append('serialized_request_data')

                    # get tags for filtering code generation
                    s2 = set(path.get('x-mechanic-tags', []))

                    if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(filter_tags) == 0:
                        VAR_PATTERN = r'{([\w_-]*)}'
                        context['codeblocks'].append({
                            'type': 'blueprint',
                            'class_name': path['x-mechanic-controller']['class_name'],
                            'base_class_name': path['x-mechanic-controller'].get('base_class_name', 'flask_restplus.Resource'),
                            'version': path.get('x-mechanic-version', oapi_version),
                            'route': re.sub(VAR_PATTERN, r'<string:\1>', path_name).replace('-', '_'),
                            'oapi': oapi_obj['paths'][path_name],
                        })
            if args['--tests']:
                for model_name, model in oapi_obj['components']['schemas'].items():
                    if model.get('allOf'):
                        allof_refs = []
                        # first assign 'model' to actual schema data, not the allOf ref
                        for item in model.get('allOf'):
                            if not item.get('$ref'):
                                model = item
                            else:
                                allof_refs.append(item.get('$ref'))

                        for allof_ref in allof_refs:
                            obj, obj_name = merger.follow_reference_link(allof_ref)
                            for prop_name, prop_obj in obj.get('properties').items():
                                model['properties'][prop_name] = prop_obj
                                if model.get('required'):
                                    for req in obj.get('required', []):
                                        if req not in model['required']:
                                            model['required'].append(req)

                    if model_name in filter_schema_name:
                        context['codeblocks'].append({
                            'type': 'tests',
                            'test_name': model.get('x-mechanic-model', {}).get('class_name', model_name),
                            'version': model.get('x-mechanic-version', oapi_version),
                            'oapi': model,
                        })

                    if not filter_schema_name:
                        s2 = set(model.get('x-mechanic-tags', []))

                        if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(
                                filter_tags) == 0:
                            context['codeblocks'].append({
                                'type': 'tests',
                                'test_name': model.get('x-mechanic-model', {}).get('class_name', model_name),
                                'version': model.get('x-mechanic-version', oapi_version),
                                'oapi': model,
                            })

        # if object_path is oapi object, generate for 'type'
        if args['--tests']:
            result = _render(pkg_resources.resource_filename(__name__, 'templates/test.tpl'), context=context)
        else:
            result = _render(pkg_resources.resource_filename(__name__, 'templates/code.tpl'), context=context)

        mechanic_save_block = None
        try:
            with open(args['<output_file>'], 'r') as f:
                current_contents = f.read()
                if len(current_contents.split('# END mechanic save #')) >= 2:
                    mechanic_save_block = current_contents.split('# END mechanic save #')[0]
        except FileNotFoundError:
            # file doesn't exist, create it below
            pass

        with open(args['<output_file>'], 'w') as f:
            if not mechanic_save_block:
                f.write(result)
            else:
                f.write(mechanic_save_block)
                mechanic_modify_block = result.split('# END mechanic save #')[1]
                f.write('# END mechanic save #')
                f.write(mechanic_modify_block)


if __name__ == '__main__':
    main()
