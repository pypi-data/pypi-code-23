{%- block coding %}
# *- coding: utf-8 -*- 
{% endblock -%}

{%- block documentation %}
""" 
{% block description %}{{description}}{% endblock %}

{{name}} - created on {{ created.replace(microsecond=0).isoformat() }}
author: {{owner.name}} ({{owner.email}})
license: {{license}}
"""
{%- endblock %}

{%- block default_imports %} 
# default imports
from __future__ import unicode_literals

import logging
from builtins import str
from future.builtins import object
{% endblock %}

{% block imports %}
{% endblock %}

{% block gettext %}

import gettext
_ = gettext.gettext

{% endblock %}

{%- block source_code %}
{% endblock %}
