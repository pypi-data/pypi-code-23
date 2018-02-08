"""Supporting methods and classes for parsing request methods from API schemas"""
import re, json
from argus_api.helpers import tests
from argus_api.helpers import http
from argus_cli.helpers.formatting import python_name_for, to_snake_case, to_safe_name, from_safe_name
from argus_api.helpers.log import log


class RequestMethod(object):
    """Container for a RequestMethod, accepts all building blocks for a request method
    parsed by any parser, and provides functionality for creating an actual python
    method as a string that can be printed to file, or load that string as an actual
    function that can be executed.

    When loaded as an executable function, this function will also have attributes
    that can be used in tests, such as @function.success(), @function.unauthorized(),
    which will intercept any calls made to the URL declared in this request method,
    and respond with a fake response.

    For example, to write a test for alarms.get_alarms, you might want to decorate
    your function with:

    @alarms.get_alarms.success()
    def my_method():
        # Receives a fake response, no call to the server will be created:
        response = alarms.get_alarms()

    This class is an ABC, meaning it should not be used in its raw form. Parsers
    should subclass RequestMethod, and are responsible for overloading _fake_response
    (to parse and generate the response object into a fake response), and for passing
    the correct arguments to initialization.

    For example, you might want to have different parsers, and therefore different ways
    of parsing request methods, e.g `class RABLRequestMethod(RequestMethod`,
    `Swagger2RequestMethod(RequestMethod)`, `class OpenAPI3RequestMethod(RequestMethod)`.
    """
    def __init__(
        self,
        url: str,
        name: str,
        method: str,
        description: str,
        parameters: dict,
        response: list = None,
        errors: list = None
    ):
        self.url = url
        self.name = to_snake_case(name)
        self.method = method.lower()
        self.description = description
        self.parameters = parameters
        self.response = {
            key["name"]: key
            for key in response
            if key and "name" in key
        } if response else {}

        self.errors = errors
        self.auth_data = {}

        # Ensure parameters are sorted so that parameters
        # with a default value come first in the list

        
        if self.parameters["all"]:
            # Sort so that all parameters that are not required come last:
            self.parameters["all"] = sorted(
                self.parameters["all"],
                key=lambda parameter: "required" not in parameter or not parameter["required"]
            )

            # Sort again so that all parameters with a default value come
            self.parameters["all"] = sorted(
                self.parameters["all"],
                key=lambda parameter: "default" in parameter
            )

            # Ensure arguments are unique by name:
            unique_parameters = []
            name_list = []
            for param in self.parameters["all"]:
                if param["name"] not in name_list:
                    unique_parameters.append(param)
                    name_list.append(param["name"])
                else:
                    log.warn("[%s] Parameter %s is not unique" % (self.name, param["name"]))

            self.parameters["all"] = unique_parameters

    

    @property
    def to_template(self) -> str:
        """Creates a function from the Request Method specification"""
        template_parameters = self.to_dict
        template = '''
        def {name}({template_function_arguments}json: bool = True, verify: bool = True, apiKey: str = "{apikey}", authentication: dict = {{}}) -> dict:
            """{docstring}
            """
            from requests import {method}
            from argus_api.exceptions import http

            url = "{url}".format({template_url_parameters})
            headers = {{
                'Content-Type': 'application/json',
                'User-Agent': '{user_agent}'
            }}

            if apiKey:
                headers["Argus-API-Key"] = apiKey
            elif authentication and isinstance(authentication, dict):
                headers.update(authentication)
            elif callable(authentication):
                headers.update(authentication(url))

            body = {{}}
            {template_body_parameters}

            response = {method}(url, json=body if body else None, verify=verify, headers=headers)

            errors = []
            if response.status_code == 401:
                raise http.AuthenticationFailedException(response)
            elif response.status_code == 403:
                raise http.AccessDeniedException(response)
            elif response.status_code == 412:
                raise http.ValidationErrorException(response)
            elif response.status_code == 404:
                raise http.ObjectNotFoundException(response)

            return response.json() if json else response
        '''.replace('\n        ', '\n').format(**template_parameters)

        return template

    def decorator_template(self, status_code: int = 200, prefix: str = "") -> str:
        """Creates a decorator for successful response and returns a
        decorator template that can be printed to file and used as a 
        function decorator to fake calls to this method.

        :param int status_code: 200, 403, 401, or 404
        :returns: String template
        """
        name = {
            "200": "success",
            "401": "unauthorized",
            "403": "forbidden",
            "404": "not_found",
        }[str(status_code)]

        template ='''
        def {name}(function):
            """Mock {url}, respond with HTTP {status_code}"""
            import requests_mock
            from {fake_response_module} import {fake_response_factory}
            def mock_response(*args, **kwargs):
                with requests_mock.Mocker(real_http=True) as mock:
                    mock.register_uri(
                        "{method}",
                        r"{url}",
                        status_code={status_code},
                        json={json}
                    )
                    return function(*args, **kwargs)
                return mock_response
            return decorator
        '''.replace('\n        ', '\n').format(
            name="%s%s" % (prefix, name),
            method=self.method.upper(),
            url=self.url_regex,
            status_code=status_code,
            fake_response_module=self._fake_response_factory().__module__,
            fake_response_factory=self._fake_response_factory().__name__,
            json="{0}({1})".format(self._fake_response_factory().__name__, str(self.response)) if 199 < status_code < 204 else "None"
        )
        return template
    
    @property
    def to_function(self) -> callable:
        """Wrapper around _as_function for retrieving a standalone function
        When this property is used, the function will be attached to the 
        fake scope 'runtime_generated_api', rather than the scope of the
        given module.
        
        To attach this function on a class, or module, use .as_method_on(cls)
        """
        return self._as_function('runtime_generated_api')
    
    @property
    def url_regex(self) -> str:
        """Returns a regex for matching the URL including its parameters"""
        url = self.url

        for parameter in self.parameters["path"]:
            if parameter["type"] == 'int':
                url = url.replace("{%s}" % parameter["name"], "\d+")
            else:
                url = url.replace("{%s}" % parameter["name"], "\w+")

        return url

    @property
    def to_dict(self) -> dict:
        """Returns the request method as a dict that can be used for
        templating
        """
        return dict(
            name=self.name,
            description=self.description,
            # Create an argument string with annotations and default values:
            method=self.method,
            url=self.url,
            template_function_arguments=self._parameters_to_template(),
            template_body_parameters=self._body_parameters_to_template(),
            template_url_parameters=self._url_parameters_to_template(),
            docstring=self.docstring,
            user_agent=http.USER_AGENT,
            apikey="",
        )


    @property
    def docstring(self, indent: int = 4) -> str:
        """Creates the docstring for this request method by combining description, parameters,
        exceptions raised and response

        :returns: String to use as docstring
        """
        return ("\n" + " " * indent).join([
            self.description,
            '\n',
            *self._parameters_to_docstring(),
            *self._exceptions_to_docstring(),
            self._response_to_docstring()
        ])

    def to_method_on(self, cls):
        """Attaches this as a function on a class / module"""
        setattr(cls, self.name, self._as_function(cls.__module__))
        return cls

    def fake_response(self) -> dict:
        """Returns a fake response for this method

        :raises AttributeError: When the _fake_response method has not been overloaded
        :returns: A dict with fake data
        """
        return self._fake_response_factory()(self.response)

    # PRIVATE
    def _fake_response_factory(self):
        """Guard method, this method must be overridden in subclasses"""
        raise AttributeError(
            "Subclasses must override `_fake_response_factory` and"
            "return a method to generate fake responses!"
        )

    def _exceptions_to_docstring(self) -> list:
        """Creates the docstring definitions of HTTP errors, converting
        `Authentication failed` into e.g:

        :raises AuthenticationFailedException: on 401
        :returns: List of docstring definitions
        """
        return [
            ":raises {exception}: on {code}".format(
                # Capitalize Authentication failed to AuthenticationFailedException
                exception="%sException" % "".join(
                    [string.capitalize() for string in (error["description"].split(" ") if "description" in error else [])]
                ),
                code=status_code
            )
            for status_code, error in self.errors.items()
        ]

    def _response_to_docstring(self) -> str:
        """Creates a fake response for use as an example in the generated docstring"""
        return ":returns: %s " % json.dumps(self.fake_response())

    def _parameters_to_docstring(self) -> list:
        return [
            ":param %s %s: %s" % (
                param["type"] if "type" in param else "",
                param["name"],
                param["description"] if "description" in param else ""
             ) for param in self.parameters["all"]
        ]
    
    def _body_parameters_to_template(self):
        if self.parameters["body"]:
            return "".join([
                '\n    if {1}:\n        body.update({{"{0}": {1}}})\n'.format(
                    from_safe_name(parameter["name"]),
                    to_safe_name(parameter["name"])
                 ) for parameter in self.parameters["body"]
            ])
        return ""

    def _url_parameters_to_template(self):
        """Creates the string representation of URL parameters to be used in a 
        template string dict, e.g: `id=id, param=param, keywords=keywords`

        :returns: String formatted for printing inside a dict { } for templates
        """
        return ", ".join([
            "{0}={1}".format(
                from_safe_name(parameter["name"]),
                to_safe_name(parameter["name"])
            ) for parameter in self.parameters["path"]
        ])


    def _parameters_to_template(self) -> str:
        """Creates an annotated argument string with all the parameters for this method,
        to be used in the function signature of a template string

        :returns: Annotated function string, e.g id: int, name: str = "", keywords: list = []
        """
        def _annotate_parameter(parameter: dict) -> str:
            """Formats a parameter for printing inside a string, e.g param: str = 'default'
            
            :returns: Annotated parameter string
            """
            parameter_string = "%s: %s" % (to_safe_name(parameter["name"]), parameter["type"] if "type" in parameter else "str")

            if "default" in parameter:
                if parameter["type"] == 'list':
                    if "items" in parameter and parameter["items"]["type"]:
                        list_item_type = parameter["items"]["type"]
                    else:
                        list_item_type = "str"
                    
                    if list_item_type == "str":
                        parameter_string += " = ['%s'] " % parameter["default"]
                    else:
                        parameter_string += " = [%s]" % parameter["default"]
                elif parameter["type"] == "int":
                    parameter_string += " = %s" % parameter["default"]
                else: 
                    parameter_string += " = '%s'" % parameter["default"]
            elif "required" not in parameter or not parameter["required"]:
                parameter_string += " = None"

            return parameter_string
        
        if self.parameters["all"]:
            return ", ".join(list(map(_annotate_parameter, self.parameters["all"]))) + ","
        else:
            return ""

    def __str__(self):
        """Printable representation of this object"""
        return "<RequestMethod: url=%s method=%s parameters=%s>" % \
        (self.url, self.method, ",".join([p["name"] for p in self.parameters["all"]]))


    def _as_function(self, target_module: str = 'runtime_generated_api') -> callable:
        """Calls self.to_template to create the function string,
        then loads it into the scope to ensure the method is loaded
        
        :param target_module: What scope to assign function on, e.g cls.__module__
        :returns: Callable function
        """
        # Compile the method into the imaginary runtime_generated_api module
        fake_function = compile(
            self.to_template,
            target_module,
            'exec'
        )

        # Evaluate it into fake_globals, where it'll be accessible
        fake_globals = {}
        eval(fake_function, {}, fake_globals)

        # Create a regex to match this URL, including its URL parameters
        # so that the decorators can intercept calls to this URL
        url_regex = self.url_regex
        function = fake_globals[self.name]

        # Successful response decorator
        function.success = tests.response(
            re.compile(url_regex),
            method=self.method,
            json=self.fake_response()
        )

        # Unauthorized 401 response decorator
        function.unauthoried = tests.response(
            re.compile(url_regex),
            method=self.method,
            status_code=401
        )

        # Access denied 403 response decorator
        function.access_denied = tests.response(
            re.compile(url_regex), 
            method=self.method, 
            status_code=403
        )

        # Not found 404 response decorator
        function.not_found = tests.response(
            re.compile(url_regex), 
            method=self.method, 
            status_code=404
        )

        return function

