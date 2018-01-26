#    Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


class Registry(object):
    impls = dict()

    """Allow domain objects to be loaded by name."""
    def __getattr__(self, name):
        return self.impls[name]

    def add(self, interface, cls):
        """Register an implementation for a class."""
        self.impls[interface.__name__] = cls

    def clear(self):
        """Deregister all implementations."""
        self.impls.clear()
