from DustCli.utils.projectTemplate import tempPath, customTempPath, ProjectTemplate
from pathlib import Path
from datetime import datetime
import shutil
import os
import re
from pbxproj import XcodeProject

iOSMap = {
    "name": "%{SCFEE_Template_Project_Name}%",
    "author": "%{SCFEE_Template_Author}%",
    "createDate": "%{SCFEE_Template_Create_Date}%",
    "displayName": "%{SCFEE_Template_Display_Name}%"
}

androidMap = {
}


class AndroidGenerator:
    def generate(self):
        pass


class iOSGenerator:
    def __init__(self, name, display, lang, plugins):
        self.name = name
        self.target = str(Path.home().joinpath('Desktop', self.name))
        self.display = display
        self.lang = lang
        self.plugins = plugins
        self.author = os.getlogin()
        self.date = datetime.now().strftime("%Y-%m-%d")

    def _temp_path(self):
        custom = customTempPath.joinpath('iOS', self.lang, iOSMap["name"])
        default = tempPath.joinpath('iOS', self.lang, iOSMap["name"])
        if custom.is_dir():
            return str(custom)
        elif default.is_dir():
            return str(default)
        else:
            ProjectTemplate.clone_if_need()
            return str(default)

    def generate(self):
        temp = self._temp_path()
        shutil.copytree(temp, self.target)
        [self._process(str(path)) for path in Path(self.target).rglob('*')]

        self.project = XcodeProject.load(self.target + '/%s.xcodeproj/project.pbxproj' % self.name)
        [self._handle_plugin(plugin) for plugin in self.plugins if plugin.need]

        os.system('cd %s && pod install && open %s.xcworkspace' % (self.target, self.name))

    def _process(self, _path):
        path = Path(_path)
        target_path = Path(_path.replace(iOSMap["name"], self.name))
        path.rename(target_path)

        if target_path.is_file():
            content = target_path.read_text()

            content = content.replace(iOSMap["name"], self.name)
            content = content.replace(iOSMap["displayName"], self.display)
            content = content.replace(iOSMap["author"], self.author)
            content = content.replace(iOSMap["createDate"], self.date)
            target_path.write_text(content)

    def _handle_plugin(self, plugin):
        pod_path = Path.home().joinpath('Desktop', self.name, 'Podfile')
        pod_file = pod_path.read_text().replace('end', '')
        for pod in plugin.pod:
            pod_file += '  pod \'%s\'\n' % pod
        pod_file += 'end\n'
        pod_path.write_text(pod_file)

        delegate_path = Path.home() \
            .joinpath('Desktop',
                      self.name,
                      self.name,
                      'AppDelegate.%s' % (('m', 'swift')[plugin.lang == 'Swift']))
        with open(str(delegate_path), 'r') as f:
            delegate_lines = f.readlines()
        functions = iOSGenerator._process_code(str(plugin.code_path))
        delegate_lines = ['import %s\n' % _import for _import in plugin.imports] + delegate_lines
        for func in plugin.func:
            func_name = func.name
            # 找到方法名对应的内容
            func_content = [func_lines for func_lines in functions if func_name in func_lines[0]][0]
            # 如果内容不存在直接返回
            if not func_content:
                continue

            matches = [line for line in delegate_lines if func_name in line]
            if len(matches) > 0:
                # 将方法内容插入现有的方法中
                for line in matches:
                    index = delegate_lines.index(line)
                    delegate_lines = delegate_lines[0:index + 1] + func_content[1:-1] + delegate_lines[index + 1:]
            else:
                # 将方法插入 appdelegate 最底部
                delegate_lines = delegate_lines[0:-2] + func_content + delegate_lines[-2:]

                # 在 didFinishLaunch 方法中插入调用
                flag = ('return YES', 'return true')[plugin.lang == 'Swift']
                line = [line for line in delegate_lines if flag in line][0]
                index = delegate_lines.index(line)
                delegate_lines.insert(index, func.ios_desc(plugin.lang == 'Swift') + '\n')
            if plugin.lang == 'Swift':
                delegate_path.write_text(''.join(delegate_lines))

        if len(plugin.files) > 0:
            parent = self.project.get_groups_by_name(self.name)[0]
            group = self.project.add_group(plugin.name, parent=parent)
        for file in plugin.files:
            self.project.add_file(str(plugin.file_path(file)), group)
            import_h = '#import \'%s.h\'\n' % plugin.file_path(file).stem
            if plugin.lang == 'Objective-C' and import_h not in delegate_lines:
                delegate_lines.insert(0, import_h)

        if plugin.lang != 'Swift':
            delegate_path.write_text(''.join(delegate_lines))
        self.project.save()

    @staticmethod
    def _process_code(path):
        with open(path, 'r') as f:
            lines = f.readlines()

        funcs = []
        lefts = None
        temp = []
        for line in lines:
            if re.match('^\s$', line):
                continue
            if '{' in line:
                if lefts is None:
                    lefts = []
                lefts.append(len(lefts) + 1)
            if '}' in line:
                if lefts is None or len(lefts) == 0:
                    return []
                lefts.pop()
            if not line.endswith('\n'):
                line += '\n'
            temp.append(line)
            if lefts is not None and len(lefts) == 0:
                funcs.append(temp)
                temp = []
                lefts = None

        return funcs
