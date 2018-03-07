import json

import unittest

from flask import Flask
from .flask_stride import Stride
from .module import Module

class StrideTests(unittest.TestCase):

    def route_to_function_mapping(self):
        """Link an URL route rule (e.g. '/app-descriptor.json') to a view function."""
        url_rules = {}
        for r in self.app.url_map.iter_rules():
            url_rules[r.rule] = self.app.view_functions[r.endpoint]
        return url_rules

    # Initialise Stride object with different parameter combos
    def init_default(self):
        """Create a Stride object using the default values."""
        self.stride = Stride()

    def init_with_key(self):
        """Create a Stride object using the default values."""
        self.stride = Stride(key='stride-bot-key')

    def init_with_prefix(self):
        """Create a Stride object using the default values."""
        self.stride = Stride(url_prefix='/prefix')

    def init_with_app(self):
        """Create a Stride object using the default values."""
        self.stride = Stride(app=self.app)

    def init_with_key_and_prefix(self):
        self.stride = Stride(key='stride-bot-key', url_prefix='/prefix')

    def set_app_config_key(self):
        """Set the descriptor key in app.config."""
        self.app.config['STRIDE_DESCRIPTOR_KEY'] = 'DESC_KEY'

    def set_app_config_creds(self):
        """Set the Stride creds in app.config."""
        self.app.config['STRIDE_CLOUD_ID'] = 'my-cloud-id'
        self.app.config['STRIDE_CLIENT_ID'] = 'my-client-id'
        self.app.config['STRIDE_CLIENT_SECRET'] = 'my-client-secret'

    def set_app_config_descriptor_url(self):
        """Set the descriptor url in app.config."""
        self.app.config['STRIDE_DESCRIPTOR_URL'] = '/my-app-desc.json'

    def setUp(self):
        """Setup code used by all tests."""
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()
        self.init_default()
        self.set_app_config_creds()

    def test___init___with_app(self):
        """Test __init__() when `app` parameter is specified."""
        self.init_with_app()

        self.assertEqual(self.stride._blueprint.name, 'stride_None')

    def test___init___default(self):
        """Test __init__() using only default parameters."""
        self.init_default()

        self.assertEqual(self.stride._blueprint.name, 'stride_None')

    def test__get_module(self):
        """Test the _get_module() method."""
        self.init_with_key_and_prefix()
        m = Module(key='module-key')
        self.stride._add_module(m)

        modules = self.stride._get_module('module-key')

        self.assertEqual(modules, m)

    def test__add_module(self):
        """Test the _add_module() method."""
        self.init_with_key_and_prefix()
        m = Module(key='module-key')
        self.stride._add_module(m)

        modules = self.stride.modules
        expected = {m.type: [m]}

        self.assertEqual(modules, expected)

    def test__del_module(self):
        """Test the _del_module() method."""
        self.init_with_key_and_prefix()
        m = Module(key='module-key')
        self.stride._add_module(m)
        self.stride._del_module('module-key')

        modules = self.stride.modules
        expected = {}

        self.assertEqual(modules, expected)

    def test_init_app_no_key(self):
        """Test the init_app() method when no key has been specified."""
        with self.assertRaises(KeyError):
            self.stride.init_app(self.app)

    def test_init_app_no_app_config_creds(self):
        """Test what happens when no Stride creds are specified via app.config."""
        del(self.app.config['STRIDE_CLOUD_ID'])
        del(self.app.config['STRIDE_CLIENT_ID'])
        del(self.app.config['STRIDE_CLIENT_SECRET'])

        with self.assertRaises(KeyError):
            self.stride.init_app(self.app)

    def test_init_app_descriptor_url_from_config(self):
        """Test to ensure we get the descriptor url from app.config, if available."""
        self.set_app_config_key()
        self.stride.init_app(self.app)

        self.assertEqual(self.stride.stride_key, 'DESC_KEY')

    def test_init_app_key_from_config(self):
        """Test to ensure we get the app key from app.config, if available."""
        self.set_app_config_key()
        self.stride.init_app(self.app)

        self.assertEqual(self.stride.stride_key, 'DESC_KEY')
        self.assertEqual(self.stride.cloud_id, 'my-cloud-id')
        self.assertEqual(self.stride.client_id, 'my-client-id')
        self.assertEqual(self.stride.client_secret, 'my-client-secret')

    def test_init_app_descriptor_url_from_config(self):
        """Test to ensure we get the app key from app.config, if available."""
        self.set_app_config_descriptor_url()
        self.set_app_config_key()
        self.stride.init_app(self.app)

        self.assertEqual(self.stride.descriptor_path, '/my-app-desc.json')

    def test_chat_bot(self):
        """Test the chat_bot decorator function"""
        self.set_app_config_key()
        @self.stride.chat_bot('mod-key', '/mention', '/dm')
        def my_test_bot():
            print('Hooray.')

        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()

        self.assertEqual(url_rules[self.stride.url_prefix+'/mention'], my_test_bot)
        self.assertEqual(url_rules[self.stride.url_prefix+'/dm'], my_test_bot)
        self.assertIn('chat:bot', self.stride.modules)

    def test_chat_bot_messages(self):
        """Test the chat_bot_messages decorator function"""
        self.set_app_config_key()
        @self.stride.chat_bot_messages('cbm-key', 'blah, blah.*', '/cbm')
        def my_test_bot_messages():
            print('Hooray.')

        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()

        self.assertEqual(url_rules[self.stride.url_prefix+'/cbm'], my_test_bot_messages)
        self.assertIn('chat:bot:messages', self.stride.modules)

    def test_chat_webhook(self):
        """Test the chat_webhook function"""
        self.set_app_config_key()
        self.stride.chat_webhook(key='cwh-key', event='conversation:updates', url='https://my-external-site.com/web-hooks')

        self.stride.init_app(self.app)

        self.assertIn('chat:webhook', self.stride.modules)

    def test_chat_dialog(self):
        """Test the chat_dialog function"""
        self.set_app_config_key()
        @self.stride.chat_dialog(key='cd-key', title='My Dialog Box', path='/dialog-1')
        def my_test_dialog():
            print('My Dialog is AWESOME!')

        self.stride.init_app(self.app)

        self.assertIn('chat:dialog', self.stride.modules)

    def test_chat_message_action(self):
        self.set_app_config_key()
        self.stride.chat_message_action(key='cma-key', name='Do Message Stuff', target='/dialog-1')

        self.stride.init_app(self.app)

        self.assertIn('chat:messageAction', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:messageAction'][0].to_descriptor(), {'key':'cma-key', 'name': {'value': 'Do Message Stuff'}, 'target':'/dialog-1'})

    def test_chat_input_action(self):
        self.set_app_config_key()
        self.stride.chat_input_action(key='cia-key', name='Do Input Stuff', target='/dialog-1')

        self.stride.init_app(self.app)

        self.assertIn('chat:inputAction', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:inputAction'][0].to_descriptor(), {'key':'cia-key', 'name': {'value': 'Do Input Stuff'}, 'target':'/dialog-1'})

    def test_chat_external_page(self):
        self.set_app_config_key()
        self.stride.chat_external_page(key='ep-key', name='Some External Page', url='https://myexternal.page.com/some_age')

        self.stride.init_app(self.app)

        self.assertIn('chat:externalPage', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:externalPage'][0].to_descriptor(), {'key':'ep-key', 'name': {'value': 'Some External Page'}, 'url':'https://myexternal.page.com/some_age'})

    def test_chat_glance(self):
        self.set_app_config_key()
        self.stride.chat_glance(key='gl-key', name='My Glance', icon_1x='/static/glance1_1.ico', icon_2x='/static/glance1_2.ico')

        self.stride.init_app(self.app)

        self.assertIn('chat:glance', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:glance'][0].to_descriptor(), {'key':'gl-key', 'name': {'value': 'My Glance'}, 'icon':{'url':'/static/glance1_1.ico', 'url@2x':'/static/glance1_2.ico'}})

    def test_chat_glance_query(self):
        self.set_app_config_key()
        self.stride.chat_glance(key='gl-key', name='My Glance', icon_1x='/static/glance1_1.ico', icon_2x='/static/glance1_2.ico')

        @self.stride.chat_glance_query(key='gl-key', path='/gl-key-1-query')
        def my_glance_query():
            return json.dumps({'label':{'value':'blah'}})

        self.stride.init_app(self.app)

        self.assertIn('chat:glance', self.stride.modules)

        url_rules = self.route_to_function_mapping()
        query_url = self.stride.url_prefix+'/gl-key-1-query'
        self.assertIn(query_url, url_rules)

    def test_chat_sidebar(self):
        """Test the chat_sidebar function"""
        self.set_app_config_key()
        @self.stride.chat_sidebar(key='sb-key', name='My Sidebar', url='/my-sidebar-1')
        def my_test_sidebar():
            print('My sidebar is AWESOME!')

        self.stride.init_app(self.app)

        self.assertIn('chat:sidebar', self.stride.modules)

    def test_chat_configuration_url(self):
        """Test the chat_configuration_url function"""
        self.set_app_config_key()
        @self.stride.chat_configuration_url(key='cfg-key', url='/my-config-1')
        def my_test_config():
            print('My config page is AWESOME!')

        self.stride.init_app(self.app)
        self.assertIn('chat:configuration', self.stride.modules)

    def test_chat_action_target_callService(self):
        self.set_app_config_key()
        self.stride.chat_action_target(key='at-key', target='callService', parameters={'url':'/blah'})

        self.stride.init_app(self.app)

        self.assertIn('chat:actionTarget', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:actionTarget'][0].to_descriptor(), {'key':'at-key', 'callService':{'url':'/blah'}})

    def test_chat_action_target_openDialog(self):
        self.set_app_config_key()
        self.stride.chat_action_target(key='at-key', target='openDialog', parameters={'key':'dialog-key'})

        self.stride.init_app(self.app)

        self.assertIn('chat:actionTarget', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:actionTarget'][0].to_descriptor(), {'key':'at-key', 'openDialog':{'key':'dialog-key'}})

    def test_chat_action_target_openConfiguration(self):
        self.set_app_config_key()
        self.stride.chat_action_target(key='at-key', target='openConfiguration', parameters={'key': 'config-key'})

        self.stride.init_app(self.app)

        self.assertIn('chat:actionTarget', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:actionTarget'][0].to_descriptor(), {'key':'at-key', 'openConfiguration':{'key':'config-key'}})

    def test_chat_action_target_openExternalPage(self):
        self.set_app_config_key()
        self.stride.chat_action_target(key='at-key', target='openExternalPage', parameters={'key':'ext-page-key'})

        self.stride.init_app(self.app)

        self.assertIn('chat:actionTarget', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:actionTarget'][0].to_descriptor(), {'key':'at-key', 'openExternalPage':{'key':'ext-page-key'}})

    def test_chat_action_target_openSidebar(self):
        self.set_app_config_key()
        self.stride.chat_action_target(key='at-key', target='openSidebar', parameters={'key':'sidebar-key'})

        self.stride.init_app(self.app)

        self.assertIn('chat:actionTarget', self.stride.modules)
        self.assertEqual(self.stride.modules['chat:actionTarget'][0].to_descriptor(), {'key':'at-key', 'openSidebar':{'key':'sidebar-key'}})


    def test_installed_not_used(self):
        """Test when the installed  decorator function is not used"""
        self.init_with_key_and_prefix()
        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()
        installed_path = self.stride.url_prefix+'/installed'
        self.assertIn(installed_path, url_rules)
        self.assertEqual(url_rules[installed_path](), ('',204))

    def test_installed(self):
        """Test the installed  decorator function"""
        self.init_with_key_and_prefix()
        @self.stride.installed('/installed_path')
        def my_test_install():
            print('Hooray.')

        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()
        uninstalled_path = self.stride.url_prefix+'/uninstalled'
        self.assertIn(uninstalled_path, url_rules)
        self.assertEqual(url_rules[uninstalled_path](), ('',204))

    def test_uninstalled_not_used(self):
        """Test when the uninstalled  decorator function is not used"""
        self.init_with_key_and_prefix()
        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()
        self.assertIn(self.stride.url_prefix+'/uninstalled', url_rules)

    def test_uninstalled(self):
        """Test the uninstalled  decorator function"""
        self.init_with_key_and_prefix()
        @self.stride.uninstalled('/uninstalled_path')
        def my_test_uninstall():
            print('Hooray.')

        self.stride.init_app(self.app)

        url_rules = self.route_to_function_mapping()
        self.assertEqual(url_rules[self.stride.url_prefix+'/uninstalled_path'], my_test_uninstall)

    def test_app_descriptor_defaults(self):
        """Test the app_descriptor() function with mostly default values"""
        self.init_with_key_and_prefix()
        self.stride.init_app(self.app)
        descriptor_dict = json.loads(self.client.get('/prefix/app-descriptor.json').get_data())

        expected_dict = {'baseUrl': 'https://localhost/prefix', 'key': 'stride-bot-key', 'lifecycle': {'installed': '/installed', 'uninstalled': '/uninstalled'}, 'modules': {}}

        self.assertEqual(descriptor_dict, expected_dict)

    def test_app_descriptor(self):
        """Test the app_descriptor() function when all fields are modified."""

        self.init_with_key_and_prefix()
        @self.stride.installed(path='/i')
        def do_nothing():
            pass

        @self.stride.uninstalled(path='/u')
        def still_do_nothing():
            pass
      
        @self.stride.chat_bot('bot1', '/mention1', '/direct1')
        def more_doing_nothing():
            pass

        @self.stride.chat_bot_messages('cbm1', 'pattern.*', '/cbm1')
        def also_do_nothing():
            pass

        self.stride.init_app(self.app)
        descriptor_dict = json.loads(self.client.get('/prefix/app-descriptor.json').get_data())

        expected_dict = {
            'baseUrl': 'https://localhost/prefix',
            'key': 'stride-bot-key',
            'lifecycle': {
                'installed': '/i',
                'uninstalled': '/u'
            },
            'modules': {
                'chat:bot': [
                    {'key': 'bot1', 'mention': {'url': '/mention1'}, 'directMessage': {'url':'/direct1'}}
                ],
                'chat:bot:messages': [
                    {'key': 'cbm1', 'pattern': 'pattern.*', 'url': '/cbm1'}
                ]
            }
        }

        self.assertEqual(descriptor_dict, expected_dict)

if __name__ == '__main__':
    unittest.main()
