from functools import wraps
import uuid

import stride
from flask import Blueprint, request, jsonify

from .module import Module
from .chatbot import ChatBot
from .chatbotmessage import ChatBotMessage
from .chatwebhook import ChatWebhook
from .chatdialog import ChatDialog
from .chatmessageaction import ChatMessageAction
from .chatinputaction import ChatInputAction
from .chatactiontarget import ChatActionTarget
from .chatexternalpage import ChatExternalPage
from .chatglance import ChatGlance
from .chatsidebar import ChatSidebar
from .chatconfiguration import ChatConfiguration

class Stride(stride.Stride):
    def __init__(self, key=None, app=None, url_prefix=''):
        self.stride_key = key
        self.app = app
        super().__init__(cloud_id=None, client_id=None, client_secret=None)
        self.url_prefix = url_prefix
        self.lifecycle = {}
        self.modules = {}
        blueprint_name = 'stride_{}'.format(self.stride_key)
        static_file_path = '{}/static'.format(url_prefix)
        self._blueprint = Blueprint(blueprint_name, __name__, static_url_path=static_file_path)

    def init_app(self, app):
        # In case we didn't pass the Flask app in the constructor
        if app is not None:
            self.app = app

        if self.stride_key is None:
            self.stride_key = app.config['STRIDE_DESCRIPTOR_KEY']
        self.cloud_id = app.config['STRIDE_CLOUD_ID']
        self.client_id = app.config['STRIDE_CLIENT_ID']
        self.client_secret = app.config['STRIDE_CLIENT_SECRET']

        if 'STRIDE_DESCRIPTOR_URL' in app.config:
            self.descriptor_path = app.config['STRIDE_DESCRIPTOR_URL']
        else:
            self.descriptor_path = '/app-descriptor.json'

        self._blueprint.add_url_rule(self.descriptor_path, 'app_descriptor', self.app_descriptor)

        if 'installed' not in self.lifecycle:
            @self.installed()
            def installed_default():
                return ('',204)

        if 'uninstalled'  not in self.lifecycle:
            @self.uninstalled()
            def uninstalled_default():
                return ('', 204)

        # This must be done last
        self.app.register_blueprint(self._blueprint, url_prefix=self.url_prefix)

    def _get_module(self, key):
        for mod_type in self.modules:
            for m in self.modules[mod_type]:
                if m.properties['key'] == key:
                    return m
        return None

    def _add_module(self, module):
        """Register a module to the app."""
        # Make sure we are dealing with a Module object
        if not isinstance(module, Module):
            pass

        module_type = module.type
        mod_key = module.properties['key']

        # Ensure that all modules added have a unique key.
        if self._get_module(mod_key):
            raise ValueError('Module with key "{}" already exists.'.format(mod_key))


        # If this module is the first of its type, we need to add the key to the dict.
        if module_type not in self.modules:
            self.modules[module_type] = []

        self.modules[module_type].append(module)

    def _del_module(self, key):
        mod = self._get_module(key)

        # If there is no module with that key, do nothing.
        if mod is None:
            return

        mod_type = mod.type
        self.modules[mod_type].remove(mod)

        # If there are no more modules of this type, delete the type.
        if len(self.modules[mod_type]) == 0:
            del(self.modules[mod_type])

    def chat_bot(self, key=None, mention_path=None, direct_message_path=None):
        """Decorator for declaring a function to run against a chat:bot module."""
        def module_decorator(func):
            module = ChatBot(key, mention_path, direct_message_path)
            self._add_module(module)

            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            if direct_message_path is not None:
                func_wrapper = self._blueprint.route(
                    direct_message_path, methods=['POST'])(func_wrapper)
            if mention_path is not None:
                func_wrapper = self._blueprint.route(
                    mention_path, methods=['POST'])(func_wrapper)
            return func_wrapper
        return module_decorator

    def chat_bot_messages(self, key=None, pattern=None, path=None):
        """Decorator for declaring a function to run against a chat:bot:messages module."""
        def module_decorator(func):
            module = ChatBotMessage(key, pattern, path)
            self._add_module(module)

            @self._blueprint.route(path, methods=['POST'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return module_decorator

    def chat_webhook(self, key, url, event='conversation:updates'):
        """Add a webhook."""
        module = ChatWebhook(key, event, url)
        self._add_module(module)

    def chat_dialog(self, key, title, path, size=None, filter=None, hint=None, primary_action=None, secondary_actions=None):
        """Decorator for declaring a function to run against a chat:dialog module."""
        def module_decorator(func):
            module = ChatDialog(key=key, title=title, url=path, size=size, filter=filter, hint=hint, primary_action=primary_action, secondary_actions=secondary_actions)
            self._add_module(module)

            @self._blueprint.route(path, methods=['GET'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return module_decorator

    def chat_message_action(self, key, name, target, weight=None, conditions=None):
        """Add a message action."""
        module = ChatMessageAction(key, name, target, weight, conditions)
        self._add_module(module)

    def chat_input_action(self, key, name, target, weight=None, conditions=None):
        """Add a input action."""
        module = ChatInputAction(key, name, target, weight, conditions)
        self._add_module(module)

    def chat_external_page(self, key, name, url, i18n=None):
        """Add an external page."""
        module = ChatExternalPage(key=key, name=name, url=url, i18n=i18n)
        self._add_module(module)

    def chat_glance(self, key, name, icon_1x, icon_2x, i18n=None, target=None, weight=None, conditions=None):
        """Basic chat:glance object without the queryUrl field."""
        module = ChatGlance(key=key, name=name, icon_1x=icon_1x, icon_2x=icon_2x, i18n=i18n, target=target, weight=weight, conditions=conditions)
        self._add_module(module)

    def chat_glance_query(self, key, path):
        """Decorator for declaring the queryUrl endpoint of the chat:glance module."""
        def module_decorator(func):
            glance = self._get_module(key)

            if glance is None or glance.type != 'chat:glance':
                raise Error('Glance "{}" is not defined.'.format(key))

            glance.properties['queryUrl'] = path

            @self._blueprint.route(path, methods=['GET'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return module_decorator

    def chat_sidebar(self, key, name, url, icon_1x=None, icon_2x=None, i18n=None, weight=None, conditions=None):
        """Decorator for declaring a chat:sidebar module."""
        def module_decorator(func):
            module = ChatSidebar(key=key, name=name, url=url, icon_1x=icon_1x, icon_2x=icon_2x, i18n=i18n, weight=weight, conditions=conditions)
            self._add_module(module)

            @self._blueprint.route(url, methods=['GET'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return module_decorator


    def chat_configuration_url(self, key, url, external_page=False):
        """Create a chat:configuration module and declare the (external)page.url endpoint."""
        def module_decorator(func):
            if external_page:
                module = ChatConfiguration(key=key, externalpage_url=url)
            else:
                module = ChatConfiguration(key=key, page_url=url)
            self._add_module(module)

            @self._blueprint.route(url, methods=['GET'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return module_decorator

    def chat_configuration_target(self, key, target):
        """Add a chat:configuration module that points to a target."""
        module = ChatConfiguration(key=key, target=target)
        self._add_module(module)

    def chat_action_target(self, key, target, parameters={}):
        """Add a chat:actionTarget module"""
        module = ChatActionTarget(key=key, target=target, parameters=parameters)
        self._add_module(module)

    def installed(self, path='/installed'):
        """Decorator for declaring a function to run as part of the install lifecycle."""
        def installed_decorator(func):
            self.lifecycle['installed'] = path
            @self._blueprint.route(path, methods=['POST'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return installed_decorator

    def uninstalled(self, path='/uninstalled'):
        """Decorator for declaring a function to run as part of the uninstall lifecycle."""
        def uninstalled_decorator(func):
            self.lifecycle['uninstalled'] = path
            @self._blueprint.route(path, methods=['POST'])
            @wraps(func)
            def func_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return func_wrapper
        return uninstalled_decorator

    def app_descriptor(self):
        """Generate the app descriptor JSON text that Atlassian Connect is expecting."""
        descriptor = {}
        base_url = 'https://{}{}'.format(request.host, self.url_prefix)
        descriptor['baseUrl'] = base_url
        descriptor['key'] = self.stride_key
        descriptor['lifecycle'] = {}
        for lifecycle_prop in ['installed', 'uninstalled']:
            if lifecycle_prop in self.lifecycle:
                descriptor['lifecycle'][lifecycle_prop] = self.lifecycle[lifecycle_prop]
            else:
                descriptor['lifecycle'][lifecycle_prop] = '/{}'.format(lifecycle_prop)

        descriptor['modules'] = {}
        for module_type in self.modules:
          descriptor['modules'][module_type] = [ m.to_descriptor() for m in self.modules[module_type] if m is not None ]

        return jsonify(descriptor)
