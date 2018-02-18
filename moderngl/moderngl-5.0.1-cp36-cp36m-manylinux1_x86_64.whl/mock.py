'''
    Mock linters.
'''

# pylint: skip-file

__all__ = ['mgl']


class Implementation:
    def set_error_class(self, *args) -> None:
        '''
            set_error_class
        '''

    def strsize(self, *args) -> int:
        '''
            strsize
        '''

        return 0

    def create_context(self, *args) -> 'Context':
        '''
            create_context
        '''

        return (None, 0)

    def create_standalone_context(self, *args) -> 'Context':
        '''
            create_standalone_context
        '''

        return (None, 0)


mgl = Implementation()
