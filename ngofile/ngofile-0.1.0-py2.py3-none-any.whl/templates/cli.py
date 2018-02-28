# *- coding: utf-8 -*- 
{% block description -%}
"""click API for {{name}}"""
{%- endblock %}

{% block imports %}
import click
import gettext

{% for entryPointName, ci in classes.items() %}
from {{ci.moduleName}} import {{ci.name}}
{% endfor %}
{% for entryPointName, fi in functions.items() %}
from {{fi.moduleName}} import {{fi.name}}
{% endfor %}

_ = gettext.gettext
{% endblock %}

{% macro expand_click_params(fi) -%}
{% for a in fi.parameters %}
    {%- if not a.has_default %}
@click.argument('{{a.name}}')
{% else %}
@click.option('--{{a.name}}'
        {%- if a.default %}, default={% if a.default is string %}'{% endif %}{{a.default}}{% if a.default is string %}'{% endif %}{% endif -%}
        {%- if a.type %}, type={{a.type}}{% endif -%}
        {%- if a.doc %}, help=_('{{a.doc}}'){% endif -%}
        )
    {% endif %}
{% endfor %}
{%- endmacro -%}

{% block source_code %}


@click.command()
@click.argument('names', nargs=-1)
def main(names):
    click.echo(repr(names))

{% if functions|length %}
########################
# FUNCTIONS ENTRY POINTS
########################
{% endif %}

{% for entryPointName, fi in functions.items() %}
{% set params = fi.parameters|map(attribute='name') %}
@click.command()
{{ expand_click_params(fi) -}}
def {{entryPointName}}_cli(ctx,{{params| join(', ')}}):
    """ {{fi.shortDescription}} {% if fi.longDescription %}

    {{fi.longDescription}}{% endif %}"""
    {{fi.name}}({{params| join(', ')}})

{% endfor -%}

{% if classes|length %}
######################
# CLASSES ENTRY POINTS
######################

{% endif %}
{% for entryPointName, ci in classes.items() %}
# CLASS {{ci.name}}
{% set params = ci.init.parameters|map(attribute='name') %}
@click.group()
{{ expand_click_params(ci.init) -}}
@click.pass_context
def {{entryPointName}}_cli(ctx,{{params| join(', ')}}):
    """ {{ci.shortDescription}} {% if ci.longDescription %}

    {{ci.longDescription}}{% endif %}"""
    ctx.obj = {{ci.name}}({{params| join(', ')}})
    click.echo('{{ci.name}} %r' % ctx.obj)

{% set methods = ci.methods.values()|map(attribute='name') %}

{% for mi in ci.publicMethods %}
# METHOD {{mi.name}} of CLASS {{ci.name}}
{% set params = mi.parameters|map(attribute='name') %}
@{{entryPointName}}_cli.command()
{{ expand_click_params(mi) -}}
@click.pass_context
def {{mi.name}}({{params| join(', ')}}):
    """ {{mi.shortDescription}} {% if mi.longDescription %}

    {{mi.longDescription}}{% endif %}"""
    click.echo('{{mi.name}}')
    ctx.obj.{{mi.name}}({{params| join(', ')}})

{% endfor -%}

{% endfor %}
{% endblock %}
