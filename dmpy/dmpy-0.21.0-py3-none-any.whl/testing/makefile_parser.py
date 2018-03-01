import attr
import re

from dmpy.objects.dm_rule import DMRule

RULE_TARGET_DEP_REGEX = re.compile(':')
ASSIGNMENT_REGEX = re.compile('\s*:=\s*')


def extract_rules_from_makefile(lines):
    rules = []
    in_rule = False
    for line in lines:
        if in_rule:
            if line.startswith('\t'):
                rule.recipe.append(line.lstrip('\t'))
            else:
                in_rule = False
                rules.append(rule)
                continue
        if ASSIGNMENT_REGEX.search(line):
            in_rule = False
            continue
        target_deps = RULE_TARGET_DEP_REGEX.split(line)
        if len(target_deps) == 2:
            in_rule = True
            rule = DMRule(target_deps[0], target_deps[1].split())
    return rules
