from __future__ import print_function, unicode_literals

import logging
import re
import yaml
import jsonpath_ng.ext as jsonpath

from globals import *
import pathresolver

logging.basicConfig()
logger = logging.getLogger(__name__)

jsonpath.auto_id_field = '_jsonpath_id'

def resolve_path_match(match, data):
    pass

def resolve_path_multimatch(match, data):
    pass

def resolve_expression(match, data):
    pass

class TemplateResolver():
    def __init__(self):
        self.pattern_map = OrderedDict(
                ('', resolve_path_match),
                ('*', resolve_path_multimatch),
                ('!', resolve_expression),
        )
    def resolve(self, data, contextpath="$"):
        matcher = re.compile(templateregex % {"delimiter": r"\@y\!", "pathpattern": r"[^{}]+"}, re.VERBOSE|re.DOTALL)
        multimatcher = re.compile(templateregex % {"delimiter": r"\@y\!\*", "pathpattern": r"[^{}]+"}, re.VERBOSE|re.DOTALL)

def resolve_template(template, data, contextpath='$'):
    """Expand template that contains `jsonpath` expressions wrapped in form of @y!{$.my.json.path} tags.

    >>> data = {"item": [{"subitem": "First Subitem"}, {"subitem": "Second Subitem"}]}
    >>> resolve_template("Hello @y!{$.item[0].subitem} and @y!{$.item[1].subitem}", data)
    u'Hello First Subitem and Second Subitem'

    >>> resolve_template("Hello @y!*{$.item[*].subitem} and everybody else", data)
    u"Hello [u'First Subitem', u'Second Subitem'] and everybody else"
    """
    logger.debug("template: %s, contextpath: %s, data: %s" % (template, contextpath, data))
    matcher = re.compile(templateregex % {"delimiter": r"\@y\!", "pathpattern": r"[^{}]+"}, re.VERBOSE|re.DOTALL)
    multimatcher = re.compile(templateregex % {"delimiter": r"\@y\!\*", "pathpattern": r"[^{}]+"}, re.VERBOSE|re.DOTALL)
    def get_full_path(match):
        return pathresolver.resolve(match.group("braced"), contextpath)
    def _format_matchresult(matchresult):
        if isinstance(matchresult, basestring):
            return matchresult
        else:
            return yaml.dump(matchresult, **yaml_defaults)
    def resolve(match):
        path = get_full_path(match)
        if not path:
            return match.group(0)
        pathmatches = jsonpath.parse(path).find(data)
        if pathmatches:
            matchresult = pathmatches[0].value
            if len(pathmatches) > 1:
                logger.error("More than 1 match!\n\tpath: %s\n\tdata: %s" % (path, data), exc_info=True)
                return _format_matchresult(matchresult)
            elif len(pathmatches) == 1:
                return _format_matchresult(matchresult)
            else:
                return match.group(0)
        else:
            return match.group(0)
    def resolvemulti(match):
        path = get_full_path(match)
        if not path:
            return match.group(0)
        pathmatches = jsonpath.parse(path).find(data)
        return yaml.dump([m.value if pathmatches else match.group(0) for m in pathmatches], **yaml_defaults).strip()
    return multimatcher.sub(resolvemulti, matcher.sub(resolve, template))
