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

    The value is cached in the instance as _{attribute_name}. So if you
    decorate `foo` method for example, the result value will be cached
    in `self._foo` where `self` is the instance of the class which
    has the decorated method.

    Follow the doctest below for an example.

    >>> from random import randint
    >>> class OneShotDice(object):
    ...     @readonlyonce_property
    ...     def roll(self):
    ...         return randint(1, 6)

    This creates a class which it's instances property `roll` is cached
    by intance. Take a look:

    >>> dice = OneShotDice()
    >>> rolls = [dice.roll for _ in range(10)]

    Beside being random, all the values in rolls list are the same.
    >>> assert all([roll == rolls[0] for roll in rolls])

    If we create another instance the method is called again.
    >>> other_dice = OneShotDice()
    >>> other_rolls = [other_dice.roll for _ in range(10)]
    >>> assert all([roll == rolls[0] for roll in rolls])

    There is 1/10 probability of dice and other_dice have the same value.
    Let's test this.

    >>> if other_rolls[0] == rolls[0]:
    ...     # They are equal, you are lucky. So all the other values
    ...     # are equal too.
    ...     assert all([r == r_ for r in rolls for r_ in other_rolls])
    ... else:
    ...     # They differ, so all other values differ too.
    ...     assert all([r != r_ for r in rolls for r_ in other_rolls])

    Exteding works as expected because the field is cached in the instance.
    >>> class YetAnotherOneShotDice(OneShotDice):
    ...     pass
    
    >>> yet_another_dice = YetAnotherOneShotDice()
    >>> yet_another_rolls = [yet_another_dice.roll for _ in range(10)]
    >>> assert all([r == yet_another_rolls[0] for r in yet_another_rolls])

    The MRO is respected.
    >>> class Base(object):
    ...     some_attr = 'base value'
    ...     @readonlyonce_property
    ...     def attr(self):
    ...         return self.some_attr

    >>> class Child(Base):
    ...     some_attr = 'child value'

    >>> assert Base().attr == 'base value'
    >>> assert Child().attr == 'child value'
    '''


    def __init__(self, fget):
        self.attr_name = '_{}'.format(fget.__name__)
        self.fget = fget

    def __get__(self, obj, objtype):
        try:
            return getattr(obj, self.attr_name)
        except AttributeError:
            setattr(obj, self.attr_name, self.fget(obj))
            return getattr(obj, self.attr_name)




import doctest
test = doctest.DocTestSuite()
