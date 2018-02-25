"""mechanic code generator from an OpenAPI 3.0 specification file.

Usage:
    mechanic clean <openapi_file> <output_file>
    mechanic generate [--models] [--schemas] [--namespaces] [--tests] [--output-docs=<merged-file>] <openapi_file> <output_file> [--filter-tag=<tag>...] [--exclude-tag=<tag>...] [--schema=<schema_name>...]
    mechanic scaffold <openapi_file> [--output-dir=<dir>]

Options:
    -h --help                           Show this screen
    -v --version                        Show version

Examples:
    # start a new project
    mechanic scaffold <openapi_file> <output_dir>
    # generate marshmallow schemas
    mechanic generate --schemas <openapi_file> <output_file>
    # generate sqlalchemy models
    mechanic generate --models <openapi_file> <output_file>
    # generate flask-restplus namespace
    mechanic generate --namespaces <openapi_file> <output_file>
"""
# native python
import os
import pkg_resources
import datetime
import json
import copy
import re
import glob

# third party
import yaml
import yamlordereddictloader
from yamlordereddictloader import OrderedDict
from docopt import docopt

# project
from mechanic.src.merger import Merger, SpecMerger

MODELS_TPL = 'templates/scaffold/{{project_name}}/models.py.tpl'
NAMESPACE_TPL = 'templates/scaffold/{{project_name}}/namespaces/ns_{{namespace}}.py.tpl'
TESTS_TPL = 'templates/test.tpl'
REMOVE_KEYS = ['x-mechanic-controller', 'x-mechanic-db', 'x-mechanic-schema', 'x-mechanic-tags', 'x-mechanic-public',
               'x-mechanic-embeddable', 'x-mechanic-model', 'x-mechanic-db-tables', 'x-mechanic-namespace',
               'x-mechanic-name']
MECHANIC_SUPPORTED_HTTP_METHODS = ["get", "put", "post", "delete"]


def _render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    import jinja2
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or './')).get_template(filename).render(
        context)


def _write_template_to_file(tpl_path, context, output_file):
    result = _render(tpl_path, context)

    mechanic_save_block = None
    try:
        with open(output_file, 'r') as f:
            current_contents = f.read()
            if len(current_contents.split('# END mechanic save #')) >= 2:
                mechanic_save_block = current_contents.split('# END mechanic save #')[0]
    except FileNotFoundError:
        # file doesn't exist, create it below
        pass

    with open(output_file, 'w') as f:
        if not mechanic_save_block:
            f.write(result)
        else:
            f.write(mechanic_save_block)
            mechanic_modify_block = result.split('# END mechanic save #')[1]
            if not mechanic_modify_block:
                f.write('# END mechanic save #\n')
            else:
                f.write('# END mechanic save #')
            f.write(mechanic_modify_block)


def _create_directory_structure(settings, dir_name, excluded_tpl=[]):
    # create directory
    os.makedirs(dir_name, exist_ok=True)
    file_to_template = dict()

    tpl_list = glob.glob(pkg_resources.resource_filename(__name__, 'templates/scaffold/**'), recursive=True)
    output_file_list = []
    p = r'{{(.[^}]*)}}'
    for t in tpl_list:
        matches = re.findall(p, t)
        name = t
        for m in matches:
            if isinstance(settings[m], list):
                for item in settings[m]:
                    name = name.replace('{{%s}}' % m, item)
            else:
                name = name.replace('{{%s}}' % m, settings[m])
        output_file_name = name.split('templates/scaffold/')[-1].split('.tpl')[0]

        if output_file_name:
            tpl_path = 'templates/scaffold/' + t.split('templates/scaffold/')[-1]
            file_to_template['%s/%s' % (dir_name, output_file_name)] = tpl_path
            output_file_list.append(output_file_name)

    output_file_list = ['%s/%s' % (dir_name, f) for f in output_file_list]
    # sort reverse in path segment length, so longest paths create all folders first
    output_file_list.sort(key=lambda item: len(item.split('/')), reverse=True)

    for f in output_file_list:
        if os.path.dirname(f):
            os.makedirs(os.path.dirname(f), exist_ok=True)

        if not os.path.isdir(f) and file_to_template[f] not in excluded_tpl:
            _write_template_to_file(pkg_resources.resource_filename(__name__, file_to_template[f]), settings, f)


def _convert_authorization_to_swagger_format(oapi_authorizations):
    auth = dict()
    for auth_name, auth_item in oapi_authorizations.items():
        auth[auth_name] = {
            'name': 'Authorization',
            'in': 'header',
            'required': True,
            'type': 'string'
        }
    return auth


def main():
    with open(pkg_resources.resource_filename(__name__, 'VERSION')) as version_file:
        current_version = version_file.read().strip()

    args = docopt(__doc__, version=current_version)

    # if openapi_file is file, generate all of 'type' (e.g. 'model', 'schema', 'controller')
    if args['<openapi_file>'].endswith('.yaml') \
            or args['<openapi_file>'].endswith('.yml') \
            or args['<openapi_file>'].endswith('.json'):
        exclude_tag_set, filter_schema_name, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version = parse_oapi(
            args)
    else:
        raise FileNotFoundError(args['<openapi_file>'])

    if args['clean']:
        # copy openapi file
        clean_oapi = clean_oapi_obj(REMOVE_KEYS, oapi_obj)
        with open(args['<output_file>'], "w") as f:
            yaml_data = yaml.dump(OrderedDict(clean_oapi),
                                  Dumper=yamlordereddictloader.Dumper,
                                  default_flow_style=False)
            f.write(yaml_data)
    elif args['scaffold']:
        models_context = {
            'timestamp': datetime.datetime.utcnow(),
            'codeblocks': []
        }
        # get project name
        project_name = oapi_obj.get('info', {}).get('x-mechanic-name', 'project')
        dir_name = args['--output-dir'] or 'mechanic_%s' % project_name

        # get project namespaces
        namespaces = set()
        namespace_contexts = dict()
        for uri, path in oapi_obj.get('paths', {}).items():
            path_ns = path.get('x-mechanic-namespace', project_name)
            namespaces.add(path_ns)
            namespace_contexts[path_ns] = {
                'timestamp': datetime.datetime.utcnow(),
                'codeblocks': [],
                'project_name': project_name,
                'imported': [],
                'namespace': path_ns,
                'description': path.get('description', '')
            }

        exclude_templates = [
            MODELS_TPL,
            NAMESPACE_TPL
        ]
        authorizations = _convert_authorization_to_swagger_format(oapi_obj['components'].get('securitySchemes'))
        _create_directory_structure({
            'project_name': project_name,
            'namespace': list(namespaces),
            'authorizations': authorizations
        }, dir_name, excluded_tpl=exclude_templates)

        generate_models(models_context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version)
        generate_schemas(models_context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version)

        for _, c in namespace_contexts.items():
            imported = generate_namespaces(c,
                                           exclude_tag_set,
                                           filter_tag_set,
                                           filter_tags,
                                           merger,
                                           oapi_obj,
                                           oapi_version,
                                           project_name=project_name,
                                           filter_ns=c['namespace'],
                                           authorizations=authorizations)
            c['imported'] = imported
            _write_template_to_file(pkg_resources.resource_filename(__name__, NAMESPACE_TPL),
                                    c,
                                    '%s/%s/namespaces/ns_%s.py' % (dir_name, project_name, c['namespace']))

        _write_template_to_file(pkg_resources.resource_filename(__name__, MODELS_TPL),
                                models_context,
                                '%s/%s/models.py' % (dir_name, project_name))

        # copy openapi file
        clean_oapi = clean_oapi_obj(REMOVE_KEYS, oapi_obj)
        with open('%s/openapi.yaml' % (dir_name), "w") as f:
            yaml_data = yaml.dump(OrderedDict(clean_oapi),
                                  Dumper=yamlordereddictloader.Dumper,
                                  default_flow_style=False)
            f.write(yaml_data)
    elif args['generate']:
        context = {
            'timestamp': datetime.datetime.utcnow(),
            'codeblocks': []
        }
        template = 'templates/code.tpl'

        if args['--models']:
            generate_models(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version)
            template = MODELS_TPL
        if args['--schemas']:
            generate_schemas(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version)
            template = MODELS_TPL
        if args['--namespaces']:
            generate_namespaces(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version)
            template = NAMESPACE_TPL

        if (args['--models'] or args['--schemas']) and args['--namespaces']:
            template = 'templates/code.tpl'

        if args['--tests']:
            generate_tests(context, exclude_tag_set, filter_schema_name, filter_tag_set, filter_tags, merger,
                           oapi_obj, oapi_version)
            template = TESTS_TPL

        result = _render(pkg_resources.resource_filename(__name__, template), context=context)

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
                f.write('# END mechanic save #\n')
                f.write(mechanic_modify_block)


def parse_oapi(args):
    # merge oapi file
    oapi_file = args['<openapi_file>']
    if args['--output-docs']:
        output_docs = args['--output-docs']
        merger = Merger(oapi_file, output_docs)
        merger.merge()

        clean_oapi = clean_oapi_obj(REMOVE_KEYS, merger.oapi_obj)
        with open(output_docs, "w") as f:
            if output_docs.endswith(".json"):
                json_data = json.dumps(clean_oapi, indent=3)
                f.write(json_data)
            elif output_docs.endswith(".yaml") or output_docs.endswith(".yml"):
                yaml_data = yaml.dump(OrderedDict(clean_oapi),
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
    return exclude_tag_set, filter_schema_name, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version


def clean_oapi_obj(remove_keys, oapi_obj):
    m_oapi_obj_copy = copy.deepcopy(oapi_obj)
    SpecMerger.clean_schema_properties(m_oapi_obj_copy)
    for rkey in remove_keys:
        SpecMerger.clean(m_oapi_obj_copy, key=rkey)
    return m_oapi_obj_copy


def generate_tests(context, exclude_tag_set, filter_schema_name, filter_tag_set, filter_tags, merger, oapi_obj,
                   oapi_version):
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


def generate_models(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version):
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
            if model.get('x-mechanic-model'):
                context['codeblocks'].append({
                    'type': 'model',
                    'class_name': model.get('x-mechanic-model', {}).get('class_name', model_name),
                    'base_class_name': model.get('x-mechanic-model', {}).get('base_class', 'db.Model'),
                    'version': model.get('x-mechanic-version', oapi_version),
                    'oapi': model,
                    'resource_name': model_name
                })


def generate_namespaces(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version, project_name=None, filter_ns=[], authorizations=None):
    paths_copy = copy.deepcopy(oapi_obj['paths'])
    imported_schemas = set()
    for path_name, path in paths_copy.items():
        if filter_ns and path.get('x-mechanic-namespace', project_name) not in filter_ns:
            continue

        # schema = path.get('x-mechanic-controller').get('schema')

        for method_name, method in path.items():
            if method_name in MECHANIC_SUPPORTED_HTTP_METHODS:
                if not oapi_obj['paths'][path_name].get('x-mechanic-controller'):
                    oapi_obj['paths'][path_name]['x-mechanic-controller'] = dict()

                if not oapi_obj['paths'][path_name]['x-mechanic-controller'].get('methods'):
                    oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'] = dict()

                if not oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'].get(method_name):
                    oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'][method_name] = dict()

                oapi_m = oapi_obj['paths'][path_name]['x-mechanic-controller']['methods'][method_name]
                oapi_m['many'] = False
                oapi_m['request_schema'] = None
                oapi_m['response_schema'] = None
                oapi_m['operationId'] = method.get('operationId', method_name + '()')
                oapi_m['parameters'] = []
                oapi_m['resource_name'] = ''
                oapi_m['auth_header'] = False

                path_security_name = oapi_obj['paths'][path_name].get('security', [])
                if not path_security_name:
                    path_security_name = oapi_obj.get('security', [])

                for name in path_security_name:
                    for s_name, s_obj in name.items():
                        security_obj = oapi_obj['components'].get('securitySchemes', {}).get(s_name, {})
                        s_type = security_obj.get('type')
                        s_scheme = security_obj.get('scheme')
                        if s_type == 'http' and s_scheme == 'bearer':
                            oapi_m['auth_header'] = True

                params = method.get('parameters', [])
                for param in params:
                    if param.get('$ref'):
                        ref = param.get('$ref')
                        param_obj, _ = merger.follow_reference_link(ref)

                        if param_obj and param_obj.get('in') == 'path':
                            oapi_m['parameters'].append({'name': param.get('name'), 'required': param.get('required')})
                    else:
                        if param.get('name'):
                            oapi_m['parameters'].append({'name': param.get('name'), 'required': param.get('required')})

                for response_code, response_obj in method.get('responses', {}).items():
                    if response_code.startswith('2'):
                        oapi_m['code'] = response_code
                        resp_schema = response_obj. \
                            get('content', {}). \
                            get('application/json', {}). \
                            get('schema', {})
                        if resp_schema.get('items') and resp_schema.get('type') == 'array':
                            oapi_m['many'] = True
                            ref = resp_schema.get('items', {}).get('$ref')
                            # ref_obj, _ = merger.follow_reference_link(ref)
                            schema_name = ref.split('/')[-1]
                            oapi_m['response_schema'] = schema_name + 'Schema'
                            oapi_m['ns_model'] = schema_name
                            imported_schemas.add(oapi_m['response_schema'])
                        else:
                            if resp_schema.get('$ref'):
                                ref = resp_schema.get('$ref')
                                # ref_obj, _ = merger.follow_reference_link(ref)
                                schema_name = ref.split('/')[-1]
                                oapi_m['response_schema'] = schema_name + 'Schema'
                                oapi_m['ns_model'] = schema_name
                                imported_schemas.add(oapi_m['response_schema'])

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
                        imported_schemas.add(oapi_m['request_schema'])
                        oapi_m['ns_body'] = schema_name
                        oapi_m['parameters'].append({'name': 'serialized_request_data', 'required': True})

        # get tags for filtering code generation
        s2 = set(path.get('x-mechanic-tags', []))

        if (not exclude_tag_set.intersection(s2) and filter_tag_set <= s2) or len(filter_tags) == 0:
            VAR_PATTERN = r'{([\w_-]*)}'
            context['codeblocks'].append({
                'type': 'namespace',
                'class_name': path.get('x-mechanic-controller', {}).get('class_name', re.sub('[^a-zA-Z0-9 \n\.]', '', path_name.title())),
                'base_class_name': path.get('x-mechanic-controller', {}).get('base_class_name', 'flask_restplus.Resource'),
                'version': path.get('x-mechanic-version', oapi_version),
                'route': re.sub(VAR_PATTERN, r'<string:\1>', path_name).replace('-', '_'),
                'oapi': oapi_obj['paths'][path_name],
                'project_name': project_name,
                'imported_schemas': list(imported_schemas)
            })
    return imported_schemas

def generate_schemas(context, exclude_tag_set, filter_tag_set, filter_tags, merger, oapi_obj, oapi_version):
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
                    'base_class_name': model.get('x-mechanic-schema', {}).get('base_class_name', 'ma.Schema'),
                    'version': model.get('x-mechanic-version', oapi_version),
                    'oapi': model,
                    'resource_name': model_name
                })


if __name__ == '__main__':
    main()
