from cement.utils import shell
from pathlib import Path
import shutil
import yaml

tempPath = Path.home().joinpath('.dust', 'ProjectTemplates')
customTempPath = Path.home().joinpath('.dust', 'CustomProjectTemplates')


class Func:
    def __init__(self, value):
        self.name = value.split(':')[0]
        self.params = value.split(':')[1:]

    @staticmethod
    def decode(array):
        return [Func(value) for value in array]

    def ios_desc(self, swift):
        if swift and len(self.params) > 0:
            params_str = ', '.join(
                [('<#%s#>' % param, '%s: <#%s#>' % (param, param))[param != '_'] for param in self.params])
            return '%s(%s)' % (self.name, params_str)
        elif swift and len(self.params) <= 0:
            return '%s()' % self.name
        elif not swift and len(self.params) > 0:
            params_str = ' '.join(
                ['<#%s#>' % param if param == '_' else '%s: <#%s#>' % (param, param) for param in self.params])
            return '[self %s:%s];' % (self.name, params_str)
        else:
            return '[self %s];' % self.name


class ProjectPlugin:
    @staticmethod
    def load(platform, lang):
        plugin_path = Path.home().joinpath('.dust', 'Plugins', platform, lang, 'plugins.yml')
        if not plugin_path.exists():
            return []

        with open(str(plugin_path), 'r') as stream:
            try:
                plugins = yaml.load(stream)
                return [ProjectPlugin(key, value, platform, lang) for key, value in plugins.items()]
            except yaml.YAMLError as exc:
                print(exc)
                return []

    def __init__(self, name, value, platform, lang):
        self.platform = platform
        self.lang = lang
        self.name = name
        self.desc = value['desc']
        self.code = value['code']
        self.files = value.get('file', [])
        self.pod = value['pod']
        self.imports = value.get('imports', [])
        self.func = Func.decode(value['func'])
        self.need = False

    @property
    def code_path(self):
        return Path.home().joinpath('.dust', 'Plugins', self.platform, self.lang, self.code)

    def file_path(self, filename):
        return Path.home().joinpath('.dust', 'Plugins', self.platform, self.lang, filename)


class ProjectTemplate:

    @staticmethod
    def clone():
        if tempPath.is_dir():
            shutil.rmtree(str(tempPath))
        shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', str(tempPath)])

    @staticmethod
    def clone_if_need():
        if tempPath.is_dir():
            return True
        exitcode = shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', str(tempPath)])
        return exitcode == 0

    @staticmethod
    def clone_custom_template(git):
        if Path(customTempPath).is_dir():
            shutil.rmtree(customTempPath)
        shell.exec_cmd2(['git', 'clone', git, str(customTempPath)])

    @staticmethod
    def copy_custom_template(path):
        if Path(customTempPath).is_dir():
            shutil.rmtree(customTempPath)

        shutil.copytree(path, customTempPath)

    @staticmethod
    def clean_custom_template():
        if Path(customTempPath).is_dir():
            shutil.rmtree(customTempPath)
