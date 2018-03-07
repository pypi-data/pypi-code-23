"""Basic interface to the Cloogle API"""
from enum import Enum
import json
import re
import urllib.parse, urllib.request

HOST = 'https://cloogle.org'
API = 'api.php'
USER_AGENT = 'cloogle.py'


def request(query, modules=None, libraries=None, include_builtins=None,
        include_core=None, include_apps=None, page=None,
        host=HOST, user_agent=USER_AGENT):
    params = [('str', query)]

    if modules is not None:
        params.append(('mod', ','.join(modules)))
    if libraries is not None:
        params.append(('lib', ','.join(modules)))

    if include_builtins is not None:
        params.append(('include_builtins', str(include_builtins).tolower()))
    if include_core is not None:
        params.append(('include_core', str(include_core).tolower()))
    if include_apps is not None:
        params.append(('include_apps', str(include_apps).tolower()))

    if page is not None:
        params.append(('page', page))

    url = host + '/' + API + '?' + urllib.parse.urlencode(params)

    response = urllib.request.urlopen(urllib.request.Request(url,
        headers={'User-Agent': user_agent})).read()
    results = json.loads(response.decode('utf-8'))

    return Response.from_json(results)


class Request:
    def __init__(self, name=None, unify=None, class_name=None, type_name=None,
            modules=None, libraries=None, include_builtins=None,
            include_core=None, include_apps=None, page=None):
        self.unify = unify
        self.name = name
        self.class_name = class_name
        self.type_name = type_name
        self.modules = modules
        self.libraries = libraries
        self.include_builtins = include_builtins
        self.include_core = include_core
        self.include_apps = include_apps
        self.page = page

    def perform(self, host=HOST, user_agent=USER_AGENT):
        params = []

        if self.type_name is not None:
            params.append(('str', 'type ' + self.type_name))
        elif self.class_name is not None:
            params.append(('str', 'class ' + self.type_name))
        else:
            query = '' if self.name is None else self.name
            if self.unify is not None:
                query += ' :: ' + self.unify
            params.append(('str', query))

        if self.modules is not None:
            params.append(('mod', ','.join(self.modules)))
        if self.libraries is not None:
            params.append(('lib', ','.join(self.modules)))

        if self.include_builtins is not None:
            params.append(('include_builtins', str(self.include_builtins).tolower()))
        if self.include_core is not None:
            params.append(('include_core', str(self.include_core).tolower()))
        if self.include_apps is not None:
            params.append(('include_apps', str(self.include_apps).tolower()))

        if self.page is not None:
            params.append(('page', self.page))

        url = host + '/' + API + '?' + urllib.parse.urlencode(params)

        response = urllib.request.urlopen(urllib.request.Request(url,
            headers={'User-Agent': user_agent})).read()
        results = json.loads(response.decode('utf-8'))

        return Response.from_json(results)

    @staticmethod
    def from_json(json):
        return Request(
                name=json['name'] if 'name' in json else None,
                unify=json['unify'] if 'unify' in json else None,
                class_name=json['className'] if 'className' in json else None,
                type_name=json['typeName'] if 'typeName' in json else None,
                modules=json['modules'] if 'modules' in json else None,
                libraries=json['libraries'] if 'libraries' in json else None,
                include_builtins=json['include_builtins'] if 'include_builtins' in json else None,
                include_core=json['include_core'] if 'include_core' in json else None,
                include_apps=json['include_apps'] if 'include_apps' in json else None,
                page=json['page'] if 'page' in json else None)


class CloogleReturnCode(Enum):
    SUCCESS = 0
    CACHE_HIT = 1

    NO_RESULTS = 127
    INVALID_INPUT = 128
    INVALID_NAME = 129
    INVALID_TYPE = 130

    SERVER_DOWN = 150
    ILLEGAL_METHOD = 151
    ILLEGAL_REQUEST = 152
    SERVER_TIMEOUT = 153
    DOS_PROTECTION = 154


class Response:
    def __init__(self, retrn, data, msg, more_available=None, suggestions=None):
        self.retrn = CloogleReturnCode(retrn)
        self.data = data
        self.msg = msg
        self.more_available = more_available if more_available is not None else 0
        self.suggestions = suggestions

    @staticmethod
    def from_json(json):
        suggestions = None
        if 'suggestions' in json:
            suggestions = [(Request.from_json(req), n) for req, n in json['suggestions']]
        return Response(
                retrn=json['return'],
                data=[Result.from_json(d) for d in json['data']],
                msg=json['msg'],
                more_available=json['more_available'] if 'more_available' in json else None,
                suggestions=suggestions)


class Result:
    def __init__(self, library, filename, module, distance, dcl_line=None,
            icl_line=None, name=None, builtin=None, documentation=None,
            langrep_documentation=None):
        self.library = library
        self.filename = filename
        self.module = module
        self.distance = distance
        self.dcl_line = dcl_line
        self.icl_line = icl_line
        self.name = name
        self.builtin = builtin if builtin is not None else False
        self.documentation = documentation
        self.langrep_documentation = langrep_documentation

    @staticmethod
    def from_json(json):
        if json[0] == 'ProblemResult':
            result = ProblemResult.from_json(json[1])
            result.result_type = 'Problem'
            return result

        common = json[1][0]
        result = Result(
                library=common['library'],
                filename=common['filename'],
                module=common['modul'],
                distance=common['distance'],
                dcl_line=common['dcl_line'] if 'dcl_line' in common else None,
                icl_line=common['icl_line'] if 'icl_line' in common else None,
                name=common['name'],
                builtin=common['builtin'] if 'builtin' in common else None,
                documentation=common['documentation'] if 'documentation' in common else None,
                langrep_documentation=common['langrep_documentation'] if 'langrep_documentation' in common else None)

        if json[0] == 'FunctionResult':
            result.result_type = 'Function'
            return FunctionResult.from_json(result, json[1][1])
        elif json[0] == 'TypeResult':
            result.result_type = 'Type'
            return TypeResult.from_json(result, json[1][1])
        elif json[0] == 'ClassResult':
            result.result_type = 'Class'
            return ClassResult.from_json(result, json[1][1])
        elif json[0] == 'ModuleResult':
            result.result_type = 'Module'
            return ModuleResult.from_json(result, json[1][1])
        elif json[0] == 'SyntaxResult':
            result.result_type = 'Syntax'
            return SyntaxResult.from_json(result, json[1][1])
        else:
            raise ValueError('Unknown result type "' + json[0] + '"')

    def name_in_context(self, show_module=True, show_library=True,
            show_builtin=True, show_syntax_result=True,
            show_problem_result=True):
        name = self.name()
        if isinstance(self, SyntaxResult):
            if show_syntax_result:
                name += ' (syntax)'
        elif isinstance(self, ProblemResult):
            if show_problem_result:
                name += ' (common problem)'
        elif self.builtin:
            if show_builtin:
                name += ' (builtin)'
        else:
            if show_module and not isinstance(self, ModuleResult):
                name += ' in ' + self.module
            if show_library:
                name += ' in ' + self.library
        return name

    def name(self):
        raise NotImplementedError('Only implemented by child classes')

    def representation(self):
        raise NotImplementedError('Only implemented by child classes')


class FunctionResult(Result):
    @staticmethod
    def from_json(result, json):
        result.__class__ = FunctionResult
        result.func = json['func']
        result.kind = json['kind'][0]
        result.unifier = json['unifier'] if 'unifier' in json else None
        result.required_context = json['required_context'] if 'required_context' in json else None
        result.cls = json['cls'] if 'cls' in json else None
        result.constructor_of = json['constructor_of'] if 'constructor_of' in json else None
        result.recordfield_of = json['recordfield_of'] if 'recordfield_of' in json else None
        result.generic_derivations = json['generic_derivations'] if 'generic_derivations' in json else None
        result.param_doc = json['param_doc'] if 'param_doc' in json else None
        result.generic_var_doc = json['generic_var_doc'] if 'generic_var_doc' in json else None
        result.result_doc = json['result_doc'] if 'result_doc' in json else None
        result.type_doc = json['type_doc'] if 'type_doc' in json else None
        return result

    def name(self):
        string = self.func
        if self.kind == 'Macro':
            lines = self.func.split('\n')
            string = lines[1 if 'infix' in lines[0] else 0]
        name, name2, _ = string.split(' ', 2)
        name = (name2 if name == 'generic' else name).strip()
        return name[1:-1] if name[0] == '(' else name

    def representation(self):
        return self.func


class TypeResult(Result):
    @staticmethod
    def from_json(result, json):
        result.__class__ = TypeResult
        result.type = json['type']
        result.instances = json['type_instances']
        result.derivations = json['type_derivations']
        result.field_doc = json['type_field_doc'] if 'type_field_doc' in json else None
        result.constructor_doc = json['type_constructor_doc'] if 'type_constructor_doc' in json else None
        result.representation_doc = json['type_representation_doc'] if 'type_representation_doc' in json else None
        return result

    def name(self):
        match = re.match(r'::\s*(\S+)\s+(\S*)', self.type)
        if match is None:
            return self.type
        else:
            return match.groups()[0]

    def representation(self):
        return self.type


class ClassResult(Result):
    @staticmethod
    def from_json(result, json):
        result.__class__ = ClassResult
        result.class_name = json['class_name']
        result.heading = json['class_heading']
        result.funs = json['class_funs']
        result.instances = json['class_instances']
        return result

    def name(self):
        return self.class_name

    def representation(self):
        return 'class {}\nwhere\n\t'.format(self.heading) + \
            '\n\t'.join([f.replace('\n', '\n\t') for f in self.funs])


class ModuleResult(Result):
    @staticmethod
    def from_json(result, json):
        result.__class__ = ModuleResult
        result.is_core = json['module_is_core']
        return result

    def name(self):
        return self.module

    def representation(self):
        return 'module {}'.format(self.module)


class SyntaxResult(Result):
    @staticmethod
    def from_json(result, json):
        result.__class__ = SyntaxResult
        result.title = json['syntax_title']
        result.code = json['syntax_code']
        result.examples = json['syntax_examples']
        return result

    def name(self):
        return self.title

    def representation(self):
        return '\n'.join(self.code)


class ProblemResult(Result):
    def __init__(self, key, title, description, solutions, examples):
        super().__init__(None, None, None, None)
        self.key = key
        self.title = title
        self.description = description
        self.solutions = solutions
        self.examples = examples

    @staticmethod
    def from_json(json):
        return ProblemResult(
                json['problem_key'],
                json['problem_title'],
                json['problem_description'],
                json['problem_solutions'],
                json['problem_examples'])

    def name(self):
        return self.title

    def representation(self):
        return self.description
