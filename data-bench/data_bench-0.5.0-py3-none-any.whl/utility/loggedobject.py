#
#   Copyright 2017 Intel Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#    
import logging

class LoggedObject(object):
    '''
    LoggedObject provides a logger property initialized with the
    class' name. Descended objects can then log events accessing
    this property. 

    EXAMPLE

      class LoggedFoo(LoggedObject):

        def fooTheBar(self):
          self.logger.info('informative message about Foo'ing the Bar')

        def bazTheAck(self, arg):
          if not arg:
            self.logger.debug('debugging message')

    '''

    @property
    def logger(self):
        '''
        Returns a logging.Logger whose name is the class name.
        '''
        try:
            return self._logger
        except AttributeError:
            pass
        self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
