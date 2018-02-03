from __future__ import print_function, unicode_literals

import logging
import re
import yaml
import jsonpath_ng.ext as jsonpath

from constants import *

logging.basicConfig()
logger = logging.getLogger(__name__)

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
        path = match.group("braced")
        if path and (path[0] != '$'):
            return "%s%s" % (contextpath, path)
        return path
    def resolve(match):
        path = get_full_path(match)
        if not path:
            return match.string
        pathmatches = jsonpath.parse(path).find(data)
        if pathmatches and len(pathmatches) > 1:
            logger.error("More than 1 match!\n\tpath: %s\n\tdata: %s" % (path, data), exc_info=True)
        return stringtype(pathmatches[0].value if pathmatches and len(pathmatches) else match.string)
    def resolvemulti(match):
        path = get_full_path(match)
        if not path:
            return match.string
        pathmatches = jsonpath.parse(path).find(data)
        return yaml.dump([m.value if pathmatches else match.string for m in pathmatches], default_flow_style=True).strip()
    return multimatcher.sub(resolvemulti, matcher.sub(resolve, template))
