import os
import shutil


class BaseCleaner:

    def execute(self, site):
        '''Base class must implement this method
        '''
        raise NotImplementedError('Base class of BaseCleaner must implement this method.')


class DefaultCleaner(BaseCleaner):

    def execute(self, site):
        '''Clean all the file in the 'cleanup' key
        '''
        for item in site['cleanup']:
            try:
                if os.path.isfile(item):
                    os.remove(item)

                if os.path.isdir(item):
                    shutil.rmtree(item)
            except Exception:
                pass
