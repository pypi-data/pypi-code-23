# Copyright 2018 Daniel Hilst Selli <danielhilst at gmail.com>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class readonlyonce_property(object):
    '''
    Read only once property decoator.

    This should work like @property decorator but:
    - The getter function is called only once.
    - No setter is supported.

    >>> from random import randint
    >>> class OneShotDice(object):
    ...     @readonlyonce_property
    ...     def roll(self):
    ...         return randint(1, 6)
    >>> dice = OneShotDice()
    >>> rolls = [dice.roll for _ in range(0)]
    >>> assert all([roll == rolls[0] for roll in rolls])

    The value is cached in the instance of this descriptor, in
    the `val` attribute.
    '''

    def __init__(self, fget):
        self.val = None
        self.name = fget.__name__
        self.fget = fget

    def __get__(self, obj, objtype):
        if self.val is None:
            self.val = self.fget(obj)
        return self.val




import doctest
test = doctest.DocTestSuite()
