import os
import sys
import json
import inspect
import importlib

from notes_gen.core.exceptions import ImproperlyConfiguredException
from notes_gen.core.cleaners import BaseCleaner, DefaultCleaner
from notes_gen.core.postprocessors import BasePostProcessor
from notes_gen.core.preprocessors import BasePrePorcessor, MarkdownCombiner
from notes_gen.core.renders import BaseRender, PandocRender


class ProjectSettings:
    '''Module to read project settings
    '''
    _SETTINGS_FILENAME = '_config.json'

    _FOLDER_SETTINGS = 'folders'
    _REQUIRED_FOLDER_SETTINGS = ['assets', 'public', 'layout',
                                 'notes', 'plugins']
    _PLUGINS_FOLDER_KEY = 'plugins'

    _DEFAULT_SETTINGS = {
        'root_index_page': True,
        'mathjax': True,
        'generate_html': True,
        'generate_pdf': True,
        'generate_latex': True,
        'pulgins_modules': []
    }

    _PLUGINS_MODULES_KEY = 'pulgins_modules'
    _PLUGINS_BASE_CLASSES = {
        'render': BaseRender,
        'cleaner': BaseCleaner,
        'post_processor': BasePostProcessor,
        'pre_processor': BasePrePorcessor,
    }
    _DEFAULT_PLUGINS = {
        'render': [PandocRender, ],
        'cleaner': [DefaultCleaner, ],
        'post_processor': [],
        'pre_processor': [MarkdownCombiner, ]
    }

    _error_message = {
        'file_not_found': 'Settings file is not avaliable.',
        'invalid_file_format': 'Settings file has improper format.',
        'settings_not_found': 'Required settings "{setting}" not found',
        'folder_not_found': '"{path}" folder not found.',
        'invalid_type': 'Invaild value for "{setting}" settings, expected "{expected}" but got "{got}".',
        'invalid_plugin': 'Invalid plugin "{plugin}"',
    }

    @classmethod
    def read(cls, project_folder):
        '''Read settings file, pre process the configuration and return settings
        '''
        project_folder = os.path.abspath(project_folder)

        # Read settings
        settings_file = os.path.join(project_folder, cls._SETTINGS_FILENAME)
        if os.path.exists(settings_file) is False:
            raise ImproperlyConfiguredException(cls._error_message['file_not_found'])
        with open(settings_file, 'r') as file:
            try:
                settings = json.loads(file.read())
            except json.JSONDecodeError:
                raise ImproperlyConfiguredException(cls._error_message['invalid_file_format'])

        # Add projects_folder
        settings['projects_folder'] = project_folder

        cls._check_required_settings(settings)
        cls._attach_default_settings(settings)
        cls._attach_plugins(settings)

        return settings

    @classmethod
    def _check_required_settings(cls, settings):
        '''Check for required settings
        '''
        project_folder = settings['projects_folder']

        # Check for folder setting
        folder_settings = settings.get(cls._FOLDER_SETTINGS, None)
        if folder_settings is None:
            raise ImproperlyConfiguredException(cls._error_message['settings_not_found'].format(settings=cls._FOLDER_SETTINGS))

        if type(folder_settings) != dict:
            raise ImproperlyConfiguredException(cls._error_message['invalid_type'].format(setting=cls._FOLDER_SETTINGS, expected=dict.__name__, got=type(folder_settings).__name__))

        # Check for folders
        folder_path_settings = {}
        for name in cls._REQUIRED_FOLDER_SETTINGS:
            folder_name = folder_settings.get(name, None)

            # Check if settings exits
            if folder_name is None:
                raise ImproperlyConfiguredException(cls._error_message['settings_not_found'].format(setting=name))

            # Check if folder exits
            folder_path = os.path.abspath(os.path.join(project_folder, folder_name))
            if os.path.isdir(folder_path) is False:
                raise ImproperlyConfiguredException(cls._error_message['folder_not_found'].format(path=folder_path))

            # Save folder path
            folder_path_settings[name] = folder_path

        settings[cls._FOLDER_SETTINGS] = folder_path_settings

    @classmethod
    def _attach_default_settings(cls, settings):
        '''Attached default settings if it doesnt exists
        '''
        for name, value in cls._DEFAULT_SETTINGS.items():
            setting_value = settings.get(name, value)

            # Check for user value type
            if type(setting_value) != type(value):
                msg = cls._error_message['invalid_type'].format(setting=name, expected=type(value).__name__, got=type(setting_value).__name__)
                raise ImproperlyConfiguredException(msg)

            settings[name] = setting_value

    @classmethod
    def _attach_plugins(cls, settings):
        '''Read plugins from the plugin_folder
        '''

        project_folder = settings['projects_folder']

        # To store plugins and later attach it to settings.
        plugins_settings = cls._DEFAULT_PLUGINS

        # Get pluging folder and add it to python path.
        pulgins_folder = os.path.join(project_folder, settings['folders'][cls._PLUGINS_FOLDER_KEY])
        sys.path.append(pulgins_folder)

        # Import pulings
        for file_name in settings[cls._PLUGINS_MODULES_KEY]:

            try:
                pulgin_module = importlib.import_module(file_name)
            except ModuleNotFoundError:
                msg = cls._error_message['invalid_plugin'].format(plugin=file_name)
                raise ImproperlyConfiguredException(msg)

            # Get all plugin classes from the module
            pulgin_classes = [clss for _, clss in inspect.getmembers(pulgin_module, inspect.isclass)
                              if clss.__module__ == pulgin_module.__name__]

            for clss in pulgin_classes:

                for key, base_class in cls._PLUGINS_BASE_CLASSES.items():

                    # If a class in plugin module is subclass of any base plugin class add it to settings
                    if issubclass(clss, base_class) is True:
                        plugins_settings[key].append(clss)

        # Update settings
        settings['plugins'] = plugins_settings
