'''Contains different types of logger
'''


__all__ = ['ConsoleLogger', ]


class BaseLogger(object):
    '''Subclass for all types of logger
    '''

    def warn(self, msg):
        NotImplementedError('Subclass of BaseLogger must implement warn method.')

    def success(self, msg):
        NotImplementedError('Subclass of BaseLogger must implement warn method.')

    def error(self, msg):
        NotImplementedError('Subclass of BaseLogger must implement warn method.')


class ConsoleLogger(BaseLogger):
    '''Formated logger for the console
    '''
    _COLOR_GREEN = '\033[92m'
    _COLOR_RED = '\033[91m'
    _COLOR_YELLOW = '\033[93m'

    _FONT_BOLD = '\033[1m'

    _MESSAGE_FORMAT = '{msg}...{color}{bold}[{type}]\033[0m'

    def warn(self, msg):
        '''Show a warning message at the console
        '''
        print(self._MESSAGE_FORMAT.format(color=self._COLOR_YELLOW, bold=self._FONT_BOLD,
                                          type='WARN', msg=msg))

    def success(self, msg):
        '''Show a success message at the console
        '''
        print(self._MESSAGE_FORMAT.format(color=self._COLOR_GREEN, bold=self._FONT_BOLD,
                                          type='OK', msg=msg))

    def error(self, msg):
        '''Show a error message at the console
        '''
        print(self._MESSAGE_FORMAT.format(color=self._COLOR_RED, bold=self._FONT_BOLD,
                                          type='ERROR', msg=msg))
