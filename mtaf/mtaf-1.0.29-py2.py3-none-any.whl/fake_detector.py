import re
from user_exception import UserException as Ux
import os

step_re = re.compile('''@[^(]+\(['"](.+)['"]\)''')
def_re = re.compile('\s*def\s')
doc_start_re = re.compile('\s*"""')
doc_end_re = re.compile('.*"""$')
comment_re = re.compile('#.*')
nop_re = re.compile('^pass$|^$')
re_split_parse_matcher = re.compile('{[^}]*}')
re_split_re_matcher = re.compile('\(\?p<[^>]+>[^)]+\)')
substep_re = re.compile(r"\s*context\.run_substep\((['\"])(.+)\1")
__all__ = ['FakeDetector']


class Step(object):
    def __init__(self, name):
        self.name = name
        self.fake = True
        self.substeps = []


class FakeDetector:
    def __init__(self, step_directory, fake_tag=False):
        # This module is for use by the "run_features.py" file that runs python behave feature files.
        #
        # Test steps named in the *.feature files (in the "features" directory) are implemented with python
        # code in the *.py files (in the "features/steps" directory). The purpose of this module is to detect which
        # steps have "empty" implementations, so they can be shown as "fake" steps in the test report.
        #
        # This analysis is performed in two passes.
        #
        # First pass:
        #
        #    Create a dictionary (called "steps") of all steps defined in all *.py files in the features/steps
        #    directory.
        #
        #    For each step defined in a *.py file in the features/steps directory, add a step object to the
        #    "steps" dictionary, indexed by the step name. The object will contain an attribute "fake"
        #    (initialized to True) and an attribute "substeps" (initialized to []). Then determine if the step has any
        #    "action lines" (lines with Python code other than "pass", blank lines or comments). If so, set the
        #    "fake" attribute value to False.
        #
        #    When a step implementation line has the form "context.run_substep(<substep name>)", don't treat this as
        #    an "action line" on the first pass. Instead, add the substep name to the step's "substeps" attribute.
        #
        #    In the event that run_features.py is being invoked with the "fake" tag, MockDetector.__init__ will be
        #    called with the argument "fake_tag" set to True. In this case, step function implementations that have the
        #    "@fake" decorator will be prevented from calling their step implementation code, and these steps should
        #    be considered "fake" (i.e. "fake" will remain True) with no further inspection. Because the
        #    code is not inspected, the "substeps" attribute will be an empty list even if there are run_substep lines
        #    in the step implementation.
        #
        # Second pass:
        #    For each step that has substep names, inspect the substeps (and, recursively, any substeps called by
        #    substeps) to determine if any "action lines" are called.  If so, set the "fake" attribute
        #    value to False.
        #
        # Once the MockDetector instance has been created, the "match" method will accept a step name and return True if
        # the step's "Fake" attribute is True.
        #
        self.steps = {}
        self.splits = []
        for filename in [name for name in os.listdir(step_directory) if name.endswith('.py')]:
            with open(os.path.join(step_directory, filename)) as f:
                step_key = None
                doc_zone = False
                def_zone = False
                fake_lnum = None
                def_lnum = None
                ignore_def_lines = False
                text = f.read()
                lines = text.split('\n')
                for index, line in enumerate(lines):
                    line_number = index + 1
                    line = comment_re.sub('', line)
                    line = line.strip()
                    if step_re.match(line):
                        step_key = step_re.match(line).group(1).lower()
                        def_zone = False
                        # print step_key
                        if step_key in self.steps:
                            raise Ux("duplicate step name %s:%s" % (filename, line_number + 1))
                        else:
                            self.steps[step_key] = Step(step_key)
                            self.parse_splits(step_key, line_number + 1)
                        continue
                    if step_key is None:  # before encountering the firt step, skip lines
                        continue
                    if line == "@fake":
                        fake_lnum = line_number
                        continue
                    if nop_re.match(line):
                        continue
                    if not def_zone and def_re.match(line):
                        def_lnum = line_number
                        ignore_def_lines = False
                        if fake_tag and fake_lnum is not None and fake_lnum == line_number - 1:
                            ignore_def_lines = True
                        # between the step implementation "def" and the next @step is where action lines may be found
                        def_zone = True
                        continue
                    if not ignore_def_lines:
                        # ignore doc strings (starting on line after def and enclosed in """)
                        if def_zone:
                            if line_number == def_lnum + 1 and doc_start_re.match(line):
                                doc_zone = True
                                continue
                            if doc_end_re.match(line):
                                doc_zone = False
                                continue
                            if doc_zone:
                                continue
                        if substep_re.match(line):
                            self.steps[step_key].substeps.append(substep_re.match(line).group(2).lower())
                            continue
                        self.steps[step_key].fake = False

        def get_step_key(name):
            name = ''.join(name.split('\\'))
            if name in self.steps:
                return name
            for split in self.splits:
                if re.match('[^"]*'.join(split['items']), name):
                    return split['step_name']
            raise Ux('step name "%s" not found in steps or splits' % name)

        def get_substeps(_name, _substeps):
            _step_key = get_step_key(_name)
            for _substep in self.steps[_step_key].substeps:
                substep_key = get_step_key(_substep)
                if substep_key not in _substeps:
                        _substeps.append(substep_key)
                        _substeps = get_substeps(substep_key, _substeps)
            return _substeps

        for step_key in sorted(self.steps):
            substeps = get_substeps(step_key, [])
            for substep in substeps:
                if self.steps[substep].fake is False:
                    self.steps[step_key].fake = False

    def parse_splits(self, step_name, line_number):
        items = re_split_parse_matcher.split(step_name)
        if len(items) > 1:
            # add to self.splits if the text contains a match for re_split_parse_matcher
            # but first escape '[' and ']' since we use it in a regex later
            for i in range(len(items)):
                items[i] = '\]'.join(items[i].split(']'))
                items[i] = '\['.join(items[i].split('['))
            if items in [split['items'] for split in self.splits]:
                raise Ux("duplicate split on line %d: %s" % (line_number, step_name))
            else:
                self.splits.append({'step_name': step_name, 'items': items})
        items = re_split_re_matcher.split(step_name)
        if len(items) > 1:
            # also add to self.splits if the text contains a match for re_split_re_matcher
            if items in [split['items'] for split in self.splits]:
                raise Ux("duplicate split on line %d: %s" % (line_number, step_name))
            else:
                self.splits.append({'step_name': step_name, 'items': items})

    def match(self, step_name):
        if step_name.lower() in self.steps:
            return self.steps[step_name.lower()].fake
        for split in self.splits:
            if re.match('[^"]*'.join(split['items']), step_name.lower()):
                return self.steps[split['step_name']].fake
        else:
            raise Ux("unknown step name %s" % step_name)


