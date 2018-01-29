from django import template
from django.template import TemplateSyntaxError
from django.utils.safestring import mark_safe

from django_ontology.library import OntologyLibrary
from django_ontology.models import default_ontology_model, ontology_models
from django_ontology.static import BaseStaticConcept

register = template.Library()

ONTOLOGY_LIBRARY = "ONTOLOGY_LIBRARY"
DEFAULT_MODEL = default_ontology_model()
LOAD_LEVELS = ("self", "children", "family")


class OntologyTemplateError(TemplateSyntaxError):
    pass


class UnknownKeyFormat(OntologyTemplateError):
    def __init__(self, raw_key):
        super().__init__("Cannot interpret key '%s'. It must be on the form '<parent_key>.<key>'." % raw_key)


class NotLoaded(OntologyTemplateError):
    def __init__(self, library_key):
        super().__init__("Library '%s' not loaded." % library_key)


def get_library(context, model=None):
    model_slug = model.slug if model else DEFAULT_MODEL.slug
    key = "%s_%s" % (ONTOLOGY_LIBRARY, model_slug)
    context = context.dicts[0]

    if key not in context:
        context[key] = OntologyLibrary(model=model)

    return context[key]


def load(model, context, *keys, level=None):
    library = get_library(context, model)

    if level and level not in LOAD_LEVELS:
        raise OntologyTemplateError("Unknown Load level try %s" % str(LOAD_LEVELS))

    if level == "self":
        library.load_self(*keys)
    elif level == "children":
        library.load_children(*keys)
    else:
        library.load_family(*keys)

    return ""


def load_function_builder(model):
    def _load(context, *keys, level=None):
        return load(model, context, *keys, level=level)
    return _load


for _model in ontology_models():
    register.simple_tag(func=load_function_builder(_model), takes_context=True, name="load_%s" % _model.slug)


def get_concept(context, model, item):
    library = get_library(context, model=model)

    if isinstance(item, str):
        path = item.split(".")
        key = path[-1]
        concept = library.get_or_create(key)
    elif hasattr(item, "concept"):
        concept = item.concept
    else:
        concept = item

    return concept


def write(context, item, model, expression_attr, url=None, wrap=True, extra=None):
    if not item:
        return ""

    concept = get_concept(context, model, item)

    if not concept.used_in_template:
        concept.used_in_template = True
        concept.save()

    expression = getattr(concept, expression_attr, None)
    text = str(expression) or "[{}]".format(concept.key)

    if wrap:
        text = "<{tag} key={key}{href}{extra}>{text}</{tag}>".format(
            tag="a" if url else "span",
            href=' href="%s"' % url if url else "",
            text=text,
            extra=" %s" % extra.strip() if extra else "",
            key=concept.key
        )

    text = mark_safe(text)

    return text


def write_function_builder(model, expression_attr):
    def _write(context, item, url=None, wrap=True, extra=None):
        return write(context, item, model, expression_attr, url=url, wrap=wrap, extra=extra)
    return _write


write_tags = set()
for _model in ontology_models():
    for _expression_type in _model.expression_types:
        _expression_attr = _expression_type.type
        for tag in (_expression_attr, "{model_slug}_{attr}".format(model_slug=_model.slug, attr=_expression_attr)):
            if tag in write_tags:
                continue
            write_tags.add(tag)

            register.simple_tag(func=write_function_builder(_model, _expression_attr), takes_context=True, name=tag)



