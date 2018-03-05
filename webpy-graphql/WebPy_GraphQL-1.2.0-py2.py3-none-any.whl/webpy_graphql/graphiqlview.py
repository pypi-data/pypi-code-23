import json
import web
import six
import re
import os


from werkzeug.exceptions import BadRequest, MethodNotAllowed
from graphql import Source, execute, parse, validate
from graphql.error import format_error as format_graphql_error
from graphql.error import GraphQLError
from graphql.execution import ExecutionResult
from graphql.type.schema import GraphQLSchema
from graphql.utils.get_operation_ast import get_operation_ast

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DIR_PATH = os.path.join(BASE_DIR, 'templates')

def get_accepted_content_types():
     def qualify(x):
         parts = x.split(';', 1)
         if len(parts) == 2:
             match = re.match(r'(^|;)q=(0(\.\d{,3})?|1(\.0{,3})?)(;|$)',
                              parts[1])
             if match:
                 return parts[0], float(match.group(2))
         return parts[0], 1

     raw_content_types = web.ctx.env.get('HTTP_ACCEPT', '*/*').split(',')
     qualified_content_types = map(qualify, raw_content_types)
     return list(x[0] for x in sorted(qualified_content_types,
                                      key=lambda x: x[1], reverse=True))

class HttpError(Exception):
    def __init__(self, response, message=None, *args, **kwargs):
        self.response = response
        self.message = message = message or response.description
        super(HttpError, self).__init__(message, *args, **kwargs)


class GraphiQLView:
    schema = None
    executor = None
    root_value = None
    context = None
    pretty = False
    graphiql = False
    graphiql_version = None
    graphiql_template = None
    middleware = None
    batch = False
    graphiql_version = '0.7.1'

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)

        assert not all((self.graphiql, self.batch)), 'Use either graphiql or batch processing'
        assert isinstance(self.schema, GraphQLSchema), 'A Schema is required to be provided to GraphQLView.'

    def get_root_value(self):
        return self.root_value

    def get_context(self):
        if self.context is not None:
            return self.context
        return web.ctx

    def get_middleware(self):
        return self.middleware

    def get_executor(self):
        return self.executor

    def render_graphiql(self, **kwargs):
        for key, value in kwargs.iteritems():
            if kwargs[key] and key == 'variables':
                kwargs[key] = str(json.dumps(kwargs.get(key, None)))
                continue
            kwargs[key] = json.dumps(kwargs.get(key, None))

        render = web.template.render(DIR_PATH)
        return render.graph(self.graphiql_version, **kwargs)

    def dispatch_request(self):
        try:
            if web.ctx.method.lower() not in ('get', 'post'):
                raise HttpError(MethodNotAllowed(['GET', 'POST'], 'GraphQL only supports GET and POST requests.'))

            data = self.parse_body()

            show_graphiql = self.graphiql and self.can_display_graphiql(data)

            if self.batch: # False
                responses = [self.get_response(entry) for entry in data]
                result = '[{}]'.format(','.join([response[0] for response in responses]))
                status_code = max(responses, key=lambda response: response[1])[1]
            else:
                result, status_code = self.get_response(data, show_graphiql)

            if show_graphiql:
                query, variables, operation_name, id = self.get_graphql_params(data)
                return self.render_graphiql(
                    query=query,
                    variables=json.dumps(variables),
                    operation_name=operation_name,
                    result=result
                )
            else:
                web.header('Content-Type', 'application/json')
                return result

        except HttpError as e:
            web.header('Content-Type', 'application/json')
            return self.json_encode({'errors': [self.format_error(e)]})

    def get_response(self, data, show_graphiql=False):
        query, variables, operation_name, id = self.get_graphql_params(data)

        execution_result = self.execute_graphql_request(
            data,
            query,
            variables,
            operation_name,
            show_graphiql
        )

        status_code = 200
        if execution_result:
            response = {}

            if execution_result.errors:
                response['errors'] = [self.format_error(e) for e in execution_result.errors]

            if execution_result.invalid:
                status_code = 400
            else:
                status_code = 200
                response['data'] = execution_result.data

            if self.batch:
                response = {
                    'id': id,
                    'payload': response,
                    'status': status_code,
                }

            result = self.json_encode(response, show_graphiql)
        else:
            result = None

        return result, status_code

    def execute(self, *args, **kwargs):
        return execute(self.schema, *args, **kwargs)

    def execute_graphql_request(self, data, query, variables, operation_name, show_graphiql=False):
        if not query:
            if show_graphiql:
                return None
            raise HttpError(BadRequest('Must provide query string.'))

        try:
            source = Source(query, name='GraphQL request')
            ast = parse(source)
            validation_errors = validate(self.schema, ast)
            if validation_errors:
                return ExecutionResult(
                    errors=validation_errors,
                    invalid=True,
                )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        if web.ctx.method.lower() == 'get':
            operation_ast = get_operation_ast(ast, operation_name)
            if operation_ast and operation_ast.operation != 'query':
                if show_graphiql:
                    return None
                raise HttpError(MethodNotAllowed(
                    ['POST'], 'Can only perform a {} operation from a POST request.'.format(operation_ast.operation)
                ))

        try:
            return self.execute(
                ast,
                root_value=self.get_root_value(),
                variable_values=variables or {},
                operation_name=operation_name,
                context_value=self.get_context(),
                middleware=self.get_middleware(),
                executor=self.get_executor()
            )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

    def parse_body(self):
        content_type = web.ctx.env.get('HTTP_ACCEPT')

        if content_type == 'application/graphql':
            return {'query': web.data().decode()}

        elif content_type == 'application/json':
            try:
                request_json = json.loads(web.data().decode('utf8'))
                if self.batch:
                    assert isinstance(request_json, list)
                else:
                    assert isinstance(request_json, dict)
                return request_json
            except:
                raise HttpError(BadRequest('POST body sent invalid JSON.'))

        elif content_type == 'application/x-www-form-urlencoded':
            return web.data()

        elif content_type == 'multipart/form-data':
            return web.data()

        return {}

    def json_encode(self, d, show_graphiql=False):
        pretty = self.pretty or show_graphiql or web.input().get('pretty')
        if not pretty:
            return json.dumps(d, separators=(',', ':'))

        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))

    @staticmethod
    def get_graphql_params(data):
        variables = query = id = operation_name = None

        if web.input():
            data = web.input()

        query = data.get('query', None) if web.input().get('query', None) != "undefined" else None
        variables =  data.get('variables', None) if web.input().get('variables', None) != "undefined" else None
        id = data.get('id', None) if web.input().get('id', None) != "undefined" else None
        operation_name = data.get('operationName', None) if web.input().get('operationName', None) != "undefined" else None

        if variables and isinstance(variables, six.text_type):
            try:
                variables = json.loads(variables)
            except:
                raise HttpError(BadRequest('Variables are invalid JSON.'))

        return query, variables, operation_name, id

    @classmethod
    def can_display_graphiql(cls, data):
        raw = 'raw' in web.input() or 'raw' in web.data()
        return not raw and cls.request_wants_html()

    @classmethod
    def request_wants_html(cls):

        accepted = get_accepted_content_types()
        html_index = accepted.count('text/html')
        json_index = accepted.count('application/json')

        return html_index > json_index


    @staticmethod
    def format_error(error):
        if isinstance(error, GraphQLError):
            return format_graphql_error(error)

        return {'message': six.text_type(error)}
