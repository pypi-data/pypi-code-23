'''
qsb

render_query_string: renders a QSpec into a query string.

qsb_X functions: these construct QSpec structures.

QSpec: (Search API) Query Specification structure. 
This is a Jsonable structure, made entirely of dict, list and simple types.
'''
import re
import json

def render_query_string(aQSpec):
    retval = None
    if is_string_QSpec(aQSpec):
        retval = _render_string_QSpec(aQSpec)
    elif is_unquoted_QSpec(aQSpec):
        retval = _render_unquoted_QSpec(aQSpec)
    elif is_number_QSpec(aQSpec):
        retval = _render_number_QSpec(aQSpec)
    elif is_bool_QSpec(aQSpec):
        retval = _render_bool_QSpec(aQSpec)
    elif is_field_QSpec(aQSpec):
        retval = _render_field_QSpec(aQSpec)
    elif is_and_QSpec(aQSpec):
        retval = _render_and_QSpec(aQSpec)
    elif is_or_QSpec(aQSpec):
        retval = _render_or_QSpec(aQSpec)
    elif is_not_QSpec(aQSpec):
        retval = _render_not_QSpec(aQSpec)
    elif is_paren_QSpec(aQSpec):
        retval = _render_paren_QSpec(aQSpec)
    elif is_stem_QSpec(aQSpec):
        retval = _render_stem_QSpec(aQSpec)
    elif is_eq_QSpec(aQSpec):
        retval = _render_eq_QSpec(aQSpec)
    elif is_neq_QSpec(aQSpec):
        retval = _render_neq_QSpec(aQSpec)
    elif is_lt_QSpec(aQSpec):
        retval = _render_lt_QSpec(aQSpec)
    elif is_le_QSpec(aQSpec):
        retval = _render_le_QSpec(aQSpec)
    elif is_gt_QSpec(aQSpec):
        retval = _render_gt_QSpec(aQSpec)
    elif is_ge_QSpec(aQSpec):
        retval = _render_ge_QSpec(aQSpec)
    elif is_geopoint_QSpec(aQSpec):
        retval = _render_geopoint_QSpec(aQSpec)
    elif is_distance_QSpec(aQSpec):
        retval = _render_distance_QSpec(aQSpec)
    else:
        raise ValueError("Unknown QSpec: %s" % aQSpec)
    return retval

def _render_string_QSpec(aStringQSpec):
    lstr = aStringQSpec if isunicode(aStringQSpec) else unicode(aStringQSpec, "utf-8")
    return u'"' + lstr.replace(u"\"", u"\\\"") + u'"'

def _render_unquoted_QSpec(aQSpec):
    return aQSpec.get("unquoted").replace(u"\"", u"\\\"")

def _render_number_QSpec(aQSpec):
    return unicode(aQSpec)

def _render_bool_QSpec(aQSpec):
    return u"1" if aQSpec else u"0"

def _render_field_QSpec(aQSpec):
    return NormaliseKeyForSearchAPI(aQSpec.get("fieldname")) 

def _render_and_QSpec(aQSpec):
    return u" ".join([render_query_string(lqspec) for lqspec in aQSpec.get("args")])

def _render_or_QSpec(aQSpec):
    return u" OR ".join([render_query_string(lqspec) for lqspec in aQSpec.get("args")])

def _render_not_QSpec(aQSpec):
    return u"NOT %s" % render_query_string(aQSpec.get("arg"))

def _render_paren_QSpec(aQSpec):
    return u"(%s)" % render_query_string(aQSpec.get("arg"))

def _render_stem_QSpec(aQSpec):
    return u"~%s" % render_query_string(aQSpec.get("arg"))

def _render_eq_QSpec(aQSpec):
    return u"%s:%s" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_neq_QSpec(aQSpec):
    return u"NOT (%s:%s)" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_lt_QSpec(aQSpec):
    return u"%s<%s" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_le_QSpec(aQSpec):
    return u"%s<=%s" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_ge_QSpec(aQSpec):
    return u"%s>=%s" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_gt_QSpec(aQSpec):
    return u"%s>%s" % (render_query_string(aQSpec.get("field")), render_query_string(aQSpec.get("value")))

def _render_geopoint_QSpec(aQSpec):
    return u"geopoint(%s,%s)" % (render_query_string(aQSpec.get("left")), render_query_string(aQSpec.get("right")))

def _render_distance_QSpec(aQSpec):
    return u"distance(%s,%s)" % (render_query_string(aQSpec.get("left")), render_query_string(aQSpec.get("right")))

#################################################################################

def qsb_string(aString):
    isstring(aString, True)
    lunicode = aString if isunicode(aString) else unicode(aString, "utf-8")  
    return lunicode

def qsb_unquoted(aString):
    isstring(aString, True)
    lunicode = aString if isunicode(aString) else unicode(aString, "utf-8")  
    return {
        "unquoted": lunicode
    }

def qsb_field(aFieldname):
    isstring(aFieldname, True)
    lunicode = aFieldname if isunicode(aFieldname) else unicode(aFieldname, "utf-8")  
    lunicode = NormaliseKeyForSearchAPI(lunicode)
    return {
        "fieldname": lunicode
    }

def qsb_number(aNumber):
    isnumber(aNumber, True)
    return aNumber

def qsb_bool(aBool):
    isbool(aBool, True)
    return aBool

def qsb_and(*aQSpecs):
    return {
        "op": "AND",
        "args": aQSpecs
    }

def qsb_or(*aQSpecs):
    return {
        "op": "OR",
        "args": aQSpecs
    }

def qsb_not(aQSpec):
    return {
        "op": "NOT",
        "arg": aQSpec
    }
    
def qsb_paren(aQSpec):
    return {
        "op": "paren",
        "arg": aQSpec
    }

def qsb_stem(aQSpec):
    return {
        "op": "~",
        "arg": aQSpec
    }
    
def qsb_eq(aFieldQSpec1, aValueQSpec2):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": "=",
        "field": aFieldQSpec1,
        "value": aValueQSpec2
    }

def qsb_neq(aFieldQSpec1, aValueQSpec2):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": "!=",
        "field": aFieldQSpec1,
        "value": aValueQSpec2
    }

def qsb_lt(aFieldQSpec1, aValueQSpec):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": "<",
        "field": aFieldQSpec1,
        "value": aValueQSpec
    }

def qsb_le(aFieldQSpec1, aValueQSpec):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": "<=",
        "field": aFieldQSpec1,
        "value": aValueQSpec
    }

def qsb_ge(aFieldQSpec1, aValueQSpec):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": ">=",
        "field": aFieldQSpec1,
        "value": aValueQSpec
    }

def qsb_gt(aFieldQSpec1, aValueQSpec):
    is_field_or_function_QSpec(aFieldQSpec1, True)
    return {
        "op": ">",
        "field": aFieldQSpec1,
        "value": aValueQSpec
    }

def qsb_geopoint(aNumberQSpec1, aNumberQSpec2):
    is_number_QSpec(aNumberQSpec1, True)
    is_number_QSpec(aNumberQSpec2, True)
    return {
        "op": "geopoint",
        "left": aNumberQSpec1,
        "right": aNumberQSpec2
    }

def qsb_distance(aQSpec1, aQSpec2):
    return {
        "op": "distance",
        "left": aQSpec1,
        "right": aQSpec2
    }

        
#####################################################

def is_field_or_function_QSpec(aQSpec, raises=False):
    lisfield = is_field_QSpec(aQSpec, False)
    lisfunction = is_distance_QSpec(aQSpec, False)
    retval = lisfield or lisfunction
    if not retval and raises:
        raise ValueError("field or function QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_geopoint_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "geopoint" and is_number_QSpec(aQSpec.get("left")) and is_number_QSpec(aQSpec.get("right"))
    if not retval and raises:
        raise ValueError("geopoint QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_distance_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "distance" and not (aQSpec.get("left") is None) and not (aQSpec.get("right") is None)
    if not retval and raises:
        raise ValueError("distance QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_field_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("fieldname")
    if not retval and raises:
        raise ValueError("field QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_number_QSpec(aQSpec, raises=False):
    return isnumber(aQSpec, raises)

def is_bool_QSpec(aQSpec, raises=False):
    return isbool(aQSpec, raises)

def is_string_QSpec(aQSpec, raises=False):
    retval = isstring(aQSpec)
    if not retval and raises:
        raise ValueError("string QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_unquoted_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and isunicode(aQSpec.get("unquoted"))
    if not retval and raises:
        raise ValueError("unquoted string QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_and_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "AND" and islist(aQSpec.get("args"))
    if not retval and raises:
        raise ValueError("AND QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_or_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "OR" and islist(aQSpec.get("args"))
    if not retval and raises:
        raise ValueError("OR QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_not_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "NOT" and not (aQSpec.get("arg") is None)
    if not retval and raises:
        raise ValueError("NOT QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_paren_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "paren" and not (aQSpec.get("arg") is None)
    if not retval and raises:
        raise ValueError("Paren QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def is_stem_QSpec(aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == "~" and not (aQSpec.get("arg") is None)
    if not retval and raises:
        raise ValueError("Stem QSpec expected (%s, %s)" % (aQSpec, type(aQSpec)))
    return retval

def _is_comparison_QSpec(opchar, opname, aQSpec, raises=False):
    retval = isdict(aQSpec) and aQSpec.get("op") == opchar and is_field_or_function_QSpec(aQSpec.get("field")) and (not aQSpec.get("value") is None)
    if not retval and raises:
        raise ValueError("%s QSpec expected (%s, %s)" % (opname, aQSpec, type(aQSpec)))
    return retval

def is_eq_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec("=", "Equality", aQSpec, raises)

def is_neq_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec("!=", "Inequality", aQSpec, raises)

def is_lt_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec("<", "Less-than", aQSpec, raises)

def is_le_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec("<=", "Less-than-or-equal-to", aQSpec, raises)

def is_gt_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec(">", "Greater-than", aQSpec, raises)

def is_ge_QSpec(aQSpec, raises=False):
    return _is_comparison_QSpec(">=", "Greater-than-or-equal-to", aQSpec, raises)

##########################################################################

def NormaliseKeyForSearchAPI(aRawKey):
    '''
        This method sanitizes a string that will be used in the search api as a key.
        The Search API can only take alphanumerics and underscores in keys. So, this
        method converts everything that isn't one of these into an underscore.
    '''
    lsafeRe = re.compile(u"^[A-Za-z0-9_]$")
    
    return u''.join([l if lsafeRe.match(l) else u'_' for l in aRawKey])

def isstring(aObj, raises=False):
    retval = isinstance(aObj, basestring)
    if not retval and raises:
        raise ValueError("string expected (%s, %s)" % (aObj, type(aObj)))
    return retval

def isunicode(aObj, raises=False):
    retval = isinstance(aObj, unicode)
    if not retval and raises:
        raise ValueError("unicode string expected (%s, %s)" % (aObj, type(aObj)))
    return retval

def isnumber(aObj, raises=False):
    retval = isinstance(aObj, (int, long, float)) and not isinstance(aObj, bool)
    if not retval and raises:
        raise ValueError("number expected (%s, %s)" % (aObj, type(aObj)))
    return retval

def isbool(aObj, raises=False):
    retval = isinstance(aObj, bool)
    if not retval and raises:
        raise ValueError("bool expected (%s, %s)" % (aObj, type(aObj)))
    return retval

def islist(aObj, raises=False):
    retval = isinstance(aObj, (list, tuple))
    if not retval and raises:
        raise ValueError("list expected (%s, %s)" % (aObj, type(aObj)))
    return retval

def isdict(aObj, raises=False):
    retval = isinstance(aObj, dict)
    if not retval and raises:
        raise ValueError("dict expected (%s, %s)" % (aObj, type(aObj)))
    return retval
