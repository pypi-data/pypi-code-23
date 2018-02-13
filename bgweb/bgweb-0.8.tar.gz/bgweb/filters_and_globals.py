import os
import cherrypy
from jinja2 import Environment
import jinja2.runtime


class BGWebGlobals(object):

    @staticmethod
    def load(env: Environment):
        env.globals['info_tooltip'] = info_tooltip
        env.globals['format_mutation'] = format_mutation
        env.globals['path_info'] = lambda: cherrypy.request.path_info
        env.globals['query_string'] = lambda: cherrypy.request.query_string
        env.globals['username'] = username


class BGWebFilters(object):

    @staticmethod
    def load(env: Environment):
        env.filters['reference'] = reference_link
        env.filters['to_int'] = to_int
        env.filters['basename'] = basename


def _undefined(jinja_value):
    return isinstance(jinja_value, jinja2.runtime.Undefined)


def username():
    return cherrypy.session['username'] if 'username' in cherrypy.session else None


def format_mutation(aa_change, pos):

    if _undefined(aa_change) and _undefined(pos):
        return ""

    try:
        return aa_change.replace("/", str(int(pos)))
    except :
        return ""


interactions_dict = {
    'IT': 'Indirect yarget',
    'PT': 'Primary target',
    'OR': 'Strong off-target',
    'ST': 'Mild off-target'
}


def interaction(short):
    if _undefined(short):
        return ''

    if short in interactions_dict:
       return interactions_dict[short]

    return short


def sample_driver_desc(drivers, drugged_drivers):
    drivers = len(drivers)
    drugs = len(drugged_drivers)

    return "<u>{} driver mutations</u> have been detected in this tumour sample. " \
           "{} drugs have been pescribed <u>in silico</u> based on the driver alterations in the tumor".format(drivers, drugs)


def search_examples(samples, projects=None):

    if len(samples) == 0:
        samples_str = "Sample 1, Sample 2"
    else:
        samples_str = ", ".join(s['SAMPLE'] for s in samples[0:2])

    projects_str = ""
    if projects is not None:
        if len(projects) > 0:
            projects_str = ", ".join(p['PROJECT'] for p in projects[0:2])

    return ", ".join([samples_str, projects_str])


def info_tooltip(tooltip, content="", float=""):

    if content == "":
        content = "<span class='glyphicon glyphicon-info-sign'></span>"

    if float != "":
        float = "style = 'float: {}'".format(float)

    link = '<u><span {} data-toggle="tooltip" data-placement="bottom" style="cursor: pointer;" ' \
           'title="" data-original-title="{}">{}</span></u>'.format(float, tooltip, content)

    return link


def reference_link(doi_or_pubmed):
    link = ""
    if isinstance(doi_or_pubmed, jinja2.runtime.Undefined):
        return link

    for ref in doi_or_pubmed.split(";"):
        if ":" in ref:
            split = ref.split(":")
            reference = split.pop()
            id_type = split.pop()

            if "doi" in id_type.lower():
                if link != "":
                    link += "<br/>"
                link += " DOI: <a target=\"_blank\" href=\"http://dx.doi.org/{0}\">{0}</a>".format(reference.rstrip())
            elif "pmid" in id_type.lower():
                if link != "":
                    link += "<br/>"
                link += " PMID: <a target=\"_blank\" href=\"http://www.ncbi.nlm.nih.gov/pubmed/{0}\">{0}</a>".format(reference.rstrip())
    return link


def oncodrive_role(score):
    role = 'Unclassified'

    if isinstance(score, jinja2.runtime.Undefined):
        return role

    if score < 0.3:
        role = 'Loss of function'
    elif score > 0.7:
        role = 'Activating'
    return role


def driver_sort(some_dict):
    return sorted(some_dict, key=lambda g: 1 if 'DRIVER_LABEL' in g else -1, reverse=True)


def true_to_yes(v):
    if v == 'True' or v == True or v == 'true':
        return 'Yes'
    else:
        return 'No'


def to_int(v):
    if isinstance(v, jinja2.runtime.Undefined) or v == '' or v == None:
        return 0
    else:
        return int(v)


def any_to_yes(v):
    if isinstance(v, jinja2.runtime.Undefined) or v == '' or v == None:
        return 'No'
    else:
        return 'Yes'


def basename(path):
    return os.path.basename(path)