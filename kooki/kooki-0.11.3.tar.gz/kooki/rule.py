import textwrap, yaml
from collections import OrderedDict
from kooki.exception import KookiException
from kooki.tools import write_file

invalid_field_message = textwrap.dedent('''\
    Invalid config file
    The '{1}' field of '{0}' is not in a valid format.
    It should be a {2} and it is a {3}.''')


class Rule:

    reserved = ['name', 'template', 'recipe', 'jars', 'metadata', 'content']

    def __init__(self, document_name='', config={}):
        self.document_name = document_name
        self.name = ''
        self.template = ''
        self.recipe = ''
        self.jars = []
        self.metadata = []
        self.content = []
        self.set_config(config)

    def set_config(self, config):
        for key, value in config.items():
            if key == 'name':
                if not isinstance(value, str):
                    raise KookiException(invalid_field_message.format(self.document_name, key, str, type(value)))
                self.name = value
            elif key == 'template':
                if not isinstance(value, str):
                    raise KookiException(invalid_field_message.format(self.document_name, key, str, type(value)))
                self.template = value
            elif key == 'recipe':
                if not isinstance(value, str):
                    raise KookiException(invalid_field_message.format(self.document_name, key, str, type(value)))
                self.recipe = value
            elif key == 'jars':
                if not isinstance(value, list):
                    raise KookiException(invalid_field_message.format(self.document_name, key, list, type(value)))
                self.jars += value
            elif key == 'metadata':
                if not isinstance(value, list):
                    raise KookiException(invalid_field_message.format(self.document_name, key, list, type(value)))
                self.metadata += value
            elif key == 'content':
                if not isinstance(value, list):
                    raise KookiException(invalid_field_message.format(self.document_name, key, list, type(value)))
                self.content += value

    def copy(self):
        rule = Rule()
        rule.name = self.name
        rule.template = self.template
        rule.recipe = self.recipe
        rule.jars = list(self.jars)
        rule.metadata = list(self.metadata)
        rule.content = list(self.content)
        return rule

    def export(self):

        from yaml import Loader, Dumper

        def dict_representer(dumper, data):
            return dumper.represent_dict(data.items())

        Dumper.add_representer(OrderedDict, dict_representer)

        config = OrderedDict()
        config[self.name] = OrderedDict()
        config[self.name]['name'] = self.name
        config[self.name]['template'] = self.template
        config[self.name]['recipe'] = self.recipe
        config[self.name]['jars'] = self.jars
        config[self.name]['metadata'] = self.metadata
        config[self.name]['content'] = self.content

        config_file = yaml.dump(config, Dumper=Dumper, default_flow_style=False)
        return config_file[:-1]

    def set_name(self, name, default):
        if name:
            if not isinstance(name, str):
                raise KookiException(invalid_field_message.format(self.name, 'name', str, type(name)))
            self.name = name
        else:
            self.name = default

    def set_recipe(self, recipe, default):
        if recipe:
            if not isinstance(recipe, str):
                raise KookiException(invalid_field_message.format(self.name, 'recipe', str, type(recipe)))
            self.recipe = recipe
        else:
            self.recipe = default

    def set_template(self, template, default):
        if template:
            if not isinstance(template, str):
                raise KookiException(invalid_field_message.format(self.name, 'template', str, type(template)))
            self.template = template
        else:
            self.template = default

    def set_jars(self, jars, default):
        if jars:
            if not isinstance(jars, list):
                raise KookiException(invalid_field_message.format(self.name, 'jars', list, type(jars)))
            for jar in jars:
                self.jars.append(jar)
        else:
            self.jars = default

    def set_metadata(self, metadata_list, default):
        if metadata_list:
            if not isinstance(metadata_list, list):
                raise KookiException(invalid_field_message.format(self.name, 'metadata', list, type(metadata_list)))
            for metadata in metadata_list:
                self.metadata.append(metadata)
        else:
            write_file('metadata.yaml', default)
            self.metadata.append('metadata.yaml')

    def set_content(self, content_list, default):
        if content_list:
            if not isinstance(content_list, list):
                raise KookiException(invalid_field_message.format(self.name, 'content', list, type(content_list)))
            for content in content_list:
                self.content.append(content)
        else:
            write_file('content.md', default)
            self.content.append('content.md')
