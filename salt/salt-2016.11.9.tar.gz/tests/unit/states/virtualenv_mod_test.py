# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Rahul Handay <rahulha@saltstack.com>`
'''

# Import Python Libs
from __future__ import absolute_import

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.helpers import ensure_in_syspath
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)
import os

ensure_in_syspath('../../')

# Import Salt Libs
from salt.states import virtualenv_mod

# Globals
virtualenv_mod.__salt__ = {}
virtualenv_mod.__opts__ = {}
virtualenv_mod.__env__ = {}


@patch('salt.states.virtualenv_mod.salt.utils.is_windows',
       MagicMock(return_value=True))
@patch('salt.states.virtualenv_mod.os.path.join', MagicMock(return_value=True))
@skipIf(NO_MOCK, NO_MOCK_REASON)
class VirtualenvModTestCase(TestCase):
    '''
        Validate the virtualenv_mod state
    '''
    def test_managed(self):
        '''
            Test to create a virtualenv and optionally manage it with pip
        '''
        ret = {'name': 'salt',
               'changes': {},
               'result': False,
               'comment': ''}
        ret.update({'comment': 'Virtualenv was not detected on this system'})
        self.assertDictEqual(virtualenv_mod.managed('salt'), ret)

        mock1 = MagicMock(return_value='True')
        mock = MagicMock(return_value=False)
        mock2 = MagicMock(return_value='1.1')
        with patch.dict(virtualenv_mod.__salt__, {"virtualenv.create": True,
                                                  "cp.is_cached": mock,
                                                  "cp.cache_file": mock,
                                                  "cp.hash_file": mock,
                                                  "pip.freeze": mock1,
                                                  "cmd.run_stderr": mock1,
                                                  "pip.version": mock2}):
            mock = MagicMock(side_effect=[True, True, True, False, True, True])
            with patch.object(os.path, 'exists', mock):
                ret.update({'comment': "pip requirements file"
                            " 'salt://a' not found"})
                self.assertDictEqual(virtualenv_mod.managed('salt', None,
                                                            'salt://a'), ret)

                with patch.dict(virtualenv_mod.__opts__, {"test": True}):
                    ret.update({'changes': {'cleared_packages': 'True',
                                            'old': 'True'},
                                'comment': 'Virtualenv salt is set to'
                                ' be cleared', 'result': None})
                    self.assertDictEqual(virtualenv_mod.managed('salt',
                                                                clear=1), ret)
                    ret.update({'comment': 'Virtualenv salt is already'
                                ' created', 'changes': {},
                                'result': True})
                    self.assertDictEqual(virtualenv_mod.managed('salt'), ret)

                    ret.update({'comment': 'Virtualenv salt is set to'
                                ' be created', 'result': None})
                    self.assertDictEqual(virtualenv_mod.managed('salt'), ret)

                with patch.dict(virtualenv_mod.__opts__, {"test": False}):
                    ret.update({'comment': "The 'use_wheel' option is"
                                " only supported in pip 1.4 and newer."
                                " The version of pip detected was 1.1.",
                                'result': False})
                    self.assertDictEqual(virtualenv_mod.managed('salt',
                                                                use_wheel=1),
                                         ret)

                    ret.update({'comment': 'virtualenv exists',
                                'result': True})
                    self.assertDictEqual(virtualenv_mod.managed('salt'), ret)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(VirtualenvModTestCase, needs_daemon=False)
