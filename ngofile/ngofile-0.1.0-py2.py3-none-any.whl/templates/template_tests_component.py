from pathlib import Path

from {{cookiecutter.packageName}} import *

test_file = Path(__file__).resolve()
test_dir = Path(__file__).resolve().parent


class Test{{cookiecutter.project_name}}(object):
    """ test case for {{cookiecutter.project_name}} module """

    def test_1(self):
        self.logger.warning('this is a warning msg.')
        self.assertTrue(True, msg='msg to display if it fails.')

{%- for c in package.components %}

class Test{{c.name}}(object):
    """ test case for component {{c.name}} """

    def test_1(self):
        self.logger.warning('this is a warning msg.')
        self.assertTrue(True, msg="msg to display if it fails.")
    
{% endfor %}

if __name__ == '__main__':
    unittest.main()
{% endblock %}
