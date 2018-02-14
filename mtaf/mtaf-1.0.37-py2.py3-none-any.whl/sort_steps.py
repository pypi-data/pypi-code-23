import re
from user_exception import UserException as Ux
import os

step_re = re.compile('''(@[^(]+)\(['"](\[.+\] )?(.+)['"]\)''')
def_re = re.compile('def\s+([^(]+).*(\(context[^:]*\))')


def sort(filename):
    step_defs = {}
    prefix_lines = []
    current_key = None
    with open(filename) as f:
        lines = f.readlines()
        for lnum, line in enumerate(lines):
            m = step_re.match(line)
            if m:
                # make a copy of m.groups() and replace periods with spaces
                groups = []
                for group in m.groups()[1:]:
                    if group is not None:
                        group = ' '.join(group.split('.'))
                    groups.append(group)
                step_key = '_'.join(' '.join([group.lower().translate(None, '''"'[]{}_-!\/,.*?^():+<>''') for group in groups if group is not None]).split(' '))
                if step_key in step_defs:
                    raise Ux("duplicate step name on line %s" % (lnum + 1) )
                else:
                    prefix = m.group(1)
                    if prefix != '@step':
                        line = re.sub(prefix, '@step', line)
                    step_defs[step_key] = [line]
                current_key = step_key
            else:
                if line.strip() == '@fake':
                    continue
                if current_key is None:
                    prefix_lines.append(line)
                elif def_re.match(line):
                    arglist = def_re.match(line).group(2)
                    step_defs[current_key].append('@fake\ndef ' + current_key + arglist + ':\n')
                elif len(line.strip()):
                    step_defs[current_key].append(line)
    with open(filename, 'w') as f:
        for line in prefix_lines:
            f.write(line)
        for key in sorted(step_defs.keys(), key=lambda key: ''.join(key.lower().split('"'))):
            # print ">>> " + key
            for line in step_defs[key]:
                f.write(line)
            f.write("\n\n")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps_dir", type=str, default='ePhone7/features/steps')
    args = parser.parse_args()
    for filename in [name for name in os.listdir(args.steps_dir) if name.endswith('.py')]:
        relpath = os.path.join(args.steps_dir, filename)
        print "sorting " + relpath
        sort(os.path.join(args.steps_dir, filename))
