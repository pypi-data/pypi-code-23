# -*- coding: utf-8 -*-
"""Support for multiple languages

.. module:: client.core.translator
   :platform: Windows, Unix
   :synopsis: Support for multiple languages
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from importlib import import_module

class Translator(object):
    """Class Translator
    """

    _instance_created = False
    _instance = None

    _language = ''
    _msg_mod = None
    _messages = {}

    def __init__(self, language):
        """Class constructor

        Called when object is initialized

        Args:
           language (str): language

        Raises:
           error: ValueError

        """

        if (self._instance_created == False):
            raise ValueError('For creating class instance please use the get_instance method instead!')
        if (self._instance is not None):
            raise ValueError('A Class instance already exists, use get_instance method instead!')

        if (language not in ['en', 'cs']):
            raise ValueError('Not supported language %s' % language)

        self._set_language(language)
        msg_package = 'hydratk.extensions.client.translation.' + self._language + '.messages'
        self._msg_mod = import_module(msg_package)
        self._register_messages(self._msg_mod.msg)

    @staticmethod
    def get_instance(lang=None):
        """Method gets Translator singleton instance

        Args:
            lang (str): language en|cs

        Returns:
            obj

        """

        if (Translator._instance is None):
            Translator._instance_created = True
            Translator._instance = Translator(lang)

        return Translator._instance

    def _register_messages(self, messages):
        """Methods registers langtexts

        Args:
           messages (dict): langtexts

        Returns:
           bool

        Raises:
           error: ValueError

        """

        if messages != '':
            if type(messages) is dict:
                self._messages.update(messages)
            else:
                raise ValueError('Invalid messages type, dictionary expected')
        else:
            raise ValueError('Cannot assign an empty messages, dictionary expected')
        return True

    def _set_language(self, lang):
        """Methods sets language

        Args:
           lang (str): language

        Returns:
           void

        """

        self._language = lang

    def msg(self, key, *args):
        """Methods resolves langtext according to debug level

        Args:
           key (str): langtext
           args (ags): langtext arguments

        Returns:
           str: resolved langtext

        """

        return self._messages[key].format(*args) if (key in self._messages) else key
