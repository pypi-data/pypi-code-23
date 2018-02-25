class BaseCommand(object):
    '''Base class for management commands
    '''
    description = ''

    def add_arguments(self, parser):
        '''Add default argument to the parser
        '''
        raise NotImplementedError('Subclass of BaseCommand must impelement add_arguments method.')

    def execute(self, arguments):
        '''Perform the task
        '''
        raise NotImplementedError('Subclass of BaseCommand must impelement execute method.')
