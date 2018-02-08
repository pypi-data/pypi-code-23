import re


class preprocess_element:
    parse_element = re.compile("([a-z_]+):(.*)")

    def __init__(self, num=None, title=None, params=None, input_str=None):
        if params is None:
            params = {}
        self.num = num
        self.title = title
        self.params = params

        if input_str is not None:
            self.parse_no_num(input_str)

    def parse_no_num(self, input_str):
        match = self.parse_element.match(input_str)
        self.title = match.group(1)
        params = match.group(2).split(",")
        for param in params:
            key, value = param.split("=")
            self.params[key] = value

    def get_num(self):
        return self.num

    def get_title(self):
        return self.title

    def get_params(self):
        return self.params

    def get_param(self, param):
        if param in self.params:
            return self.params[param]
        else:
            return ""

    def toString(self):
        return str(self.get_num()) + ":" + self.get_title() + ":" + ",".join(
            [k + "=" + self.get_param(k) for k in self.get_params()])
