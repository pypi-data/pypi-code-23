import os
from pybuildtool import BaseTask, make_list, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    targets = None
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        self.targets = []
        targets = make_list(cfg.get('targets'))
        for name in targets:
            self.targets.append(name.format(**self.group.get_patterns()))

        workdir = cfg.get('work_dir')
        if workdir:
            self.workdir = expand_resource(self.group, workdir)


    def perform(self):
        kwargs = {}
        if self.workdir:
            kwargs['cwd'] = self.workdir

        executable = os.environ['PYTHON_BIN']
        return self.exec_command([executable, '-m', 'unittest'] +\
                self.targets + self.args, **kwargs)
