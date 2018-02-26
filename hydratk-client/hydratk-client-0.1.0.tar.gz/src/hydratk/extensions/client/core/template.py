# -*- coding: utf-8 -*-
"""Template repository

.. module:: client.core.template
   :platform: Windows, Unix
   :synopsis: Template repository
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

proj_dir_struct = [
  '{proj_root}/lib/yodalib',
  '{proj_root}/helpers/yodahelpers',
  '{proj_root}/yoda-tests'
]

proj_files = [
  '{proj_root}/lib/yodalib/__init__.py',
  '{proj_root}/helpers/yodahelpers/__init__.py'
]

init_content = '''from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
'''

helper_content = '''# -*- coding: utf-8 -*-
"""Helper

.. module:: helpers.yodahelpers.{name}
.. moduleauthor:: Firstname Surname <email>

"""

def some_helper_function():
    pass
'''

library_content = '''# -*- coding: utf-8 -*-
"""Library

.. module:: lib.yodalib.{name}
.. moduleauthor:: Firstname Surname <email>

"""

def some_library_function():
    pass
'''

test_content = '''Test-Scenario-1:
  Id: ts_01
  Path: {path}
  Name: {name}
  Desc: Test scenario description
  Author: Firstname Surname <email>
  Version: 0.1

  Pre-Req: |
    # pre-requirements

  Test-Case-1:
    Id: tc_01
    Name: Test case name
    Desc: Test case description

    Test-Condition-1:
      Id: tco_01
      Name: Test condition name
      Desc: Test condition description

      Test: |
        # test code

      Validate: |
        # validation code
        assert True
'''

archive_content = '''# {name} '''

draft_content = '''Test-Scenario-1:
  Id: ts_01
  Path: {path}
  Name: {name}
  Desc: Test scenario description
  Author: Firstname Surname <email>
  Version: 0.1

  Pre-Req: |
    # pre-requirements

  Test-Case-1:
    Id: tc_01
    Name: Test case name
    Desc: Test case description

    Test-Condition-1:
      Id: tco_01
      Name: Test condition name
      Desc: Test condition description

      Test: |
        # test code

      Validate: |
        # validation code
        assert True
'''

condition = '''    Test-Condition-{tco_id}:
      Id: tco_{tco_id}
      Name: Test condition name
      Desc: Test condition description

      Test: |
        # test code

      Validate: |
        # validation code
        assert True
'''

case = '''  Test-Case-{tca_id}:
    Id: tc_{tca_id}
    Name: Test case name
    Desc: Test case description

''' + condition

prereq = '''  Pre-Req: |
    # pre-requirements

'''

scenario = '''Test-Scenario-{tsc_id}:
  Id: ts_{tsc_id}
  Path: {path}
  Name: Test scenario name
  Desc: Test scenario description
  Author: Firstname Surname <email>
  Version: 0.1

''' + prereq + case

postreq = '''  Post-Req: |
    # post-requirements
'''

events = '''{indent}Events:
{indent}  before_start: |
{indent}    # before code

{indent}  after_finish: |
{indent}    # after code
'''
