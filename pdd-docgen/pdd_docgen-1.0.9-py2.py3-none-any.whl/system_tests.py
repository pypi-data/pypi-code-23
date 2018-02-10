import json
import unittest


class SystemTests(unittest.TestCase):
    def setUp(self):
        self.docgen = {}
        self._docgen_description = None

    def expect(self, status, contents=None):
        self._expected_status = status
        self._expected_contents = contents
        self.docgen["status"] = status

    def explain(self, details):
        self.docgen["explanation"] = details

    def include_description(self, description):
        self._docgen_description = description

    def include_description_from(self, location):
        with open(location) as f:
            self.include_description(f.read())

    def _add_auth(self, kwargs):
        headers = kwargs.get("headers", {})
        for key, value in self.default_headers.items():
            headers[key] = value
        kwargs["headers"] = headers

    def query(
            self, method, uri, expected_status_code=200, auth=True, **kwargs):
        if auth:
            self._add_auth(kwargs)

        response = self.client.open(uri, method=method, **kwargs)
        actual_status_code = int(response.status.split(" ")[0])

        if callable(expected_status_code):
            self.assertTrue(expected_status_code(actual_status_code))
        else:
            self.assertEqual(expected_status_code, actual_status_code)

        return response, response.get_data(as_text=True)

    def delete(self, uri, expected_status_code=200, **kwargs):
        return self.query("DELETE", uri, expected_status_code, **kwargs)[0]

    def get(self, uri, expected_status_code=200, **kwargs):
        return self.query("GET", uri, expected_status_code, **kwargs)[0]

    def post(self, uri, expected_status_code=200, **kwargs):
        return self.query("POST", uri, expected_status_code, **kwargs)[0]

    def check_call(
            self, method, uri, auth=True, include_example=False,
            additional_validation=None, **kwargs):
        if auth:
            self._add_auth(kwargs)

        response, contents = self.query(
            method, uri, self._expected_status, auth, **kwargs)

        if additional_validation:
            self.assertTrue(additional_validation(response))

        if self._expected_contents is None or self._expected_contents == "":
            self.assertEqual("", contents)
        else:
            if isinstance(self._expected_contents, str):
                actual_contents = contents
            else:
                actual_contents = json.loads(contents)
                if "error" in actual_contents:
                    self.docgen["error-code"] = actual_contents["error"]

            self.assertEqual(self._expected_contents, actual_contents)

        route, variables = self._find_route(method, uri)
        self.docgen["route"] = route
        self.docgen["method"] = method

        if include_example:
            self.docgen["example"] = {
                "uri": uri,
                "options": kwargs,
                "response": actual_contents
            }

        if self._docgen_description:
            if isinstance(self._docgen_description, str):
                self.docgen["summary"] = self._docgen_description
            else:
                self.docgen["summary"] = self._docgen_description.summary
                for variable in variables:
                    if "variables" not in self.docgen:
                        self.docgen["variables"] = {}

                    v = getattr(
                        self._docgen_description, "variable_" + variable)
                    self.docgen["variables"][variable] = {
                        "description": v.description
                    }

    def _find_route(self, method, uri):
        for rule in self.app.url_map.iter_rules():
            if method in rule.methods:
                if str(rule) == uri or rule.match("|" + uri):
                    return str(rule), rule.arguments
