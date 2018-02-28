{% extends "file.py" %}
{% from 'macros_python.py' import protected_region %}
{% block description %}unit tests for {{name}}{% endblock %}

{% block imports %}
import pytest
import {{packageName}}
{% endblock %}

{% block source_code %}
class Test{{name}}():
    """ test case for {{name}} module """

    def test_1(self):
        assert True

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main(__file__)

{% endblock %}
