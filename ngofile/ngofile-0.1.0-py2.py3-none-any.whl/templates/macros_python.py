# *- coding: utf-8 -*- 

{% macro protected_region(region_id, pr_dict={}) -%}
    #/*@ PROTECTED REGION ID({{region_id}}) ENABLED START @*/
    # Insert here user code
{% if pr_dict.get(region_id) == None %}
{{ pr_dict.get(region_id,"") }}
{% endif %}
    # End of user code
    #/*@ PROTECTED REGION END @*/
{%- endmacro %}
