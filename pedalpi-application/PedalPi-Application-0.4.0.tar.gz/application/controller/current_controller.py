# Copyright 2017 SrMouraSilva
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

from application.controller.controller import Controller
from application.controller.device_controller import DeviceController
from application.dao.current_dao import CurrentDao


class CurrentPedalboardError(Exception):
    pass


class CurrentController(Controller):
    """
    Manage the current current :class:`.Pedalboard` and your bank
    """

    def __init__(self, application):
        super(CurrentController, self).__init__(application)
        self._dao = None
        self._pedalboard = None

        self._device_controller = None

        self._manager = None

    def configure(self):
        self._device_controller = self.app.controller(DeviceController)

        self._dao = self.app.dao(CurrentDao)
        self._manager = self.app.manager

        self._pedalboard = self._load_current_pedalboard()

    # ************************
    # Property
    # ************************
    @property
    def pedalboard(self):
        """
        Current :class:`.Pedalboard`

        :getter: Current pedalboard
        :setter: Set the current pedalboard (calling :meth:`.set_pedalboard`)
        """
        return self._pedalboard

    @pedalboard.setter
    def pedalboard(self, pedalboard):
        self.set_pedalboard(pedalboard)

    def set_pedalboard(self, pedalboard, notify=True, force=False):
        """
        Set the current :class:`.Pedalboard` for the pedalboard
        only if the ``pedalboard != current_pedalboard or force``

        Is also possible unload the current pedalboard data with replacing it for ``None``::

            >>> current_controller.set_pedalboard(None)

        .. warning::

            Changing the current pedalboard to Nonw, will not be able to call
            methods to change the pedalboard based in the current, like
            :meth:`.to_before_pedalboard`, :meth:`.to_next_pedalboard`,
            :meth:`.to_before_bank` and :meth:`.to_next_bank`

        :param Pedalboard pedalboard: New current pedalboard
        :param bool notify: If false, not notify change for :class:`.UpdatesObserver`
                            instances registered in :class:`.Application`
        :param bool force: Force set pedalboard
        """
        if pedalboard is not None and pedalboard.bank is None:
            raise CurrentPedalboardError('Pedalboard {} has not added in any bank'.format(pedalboard))

        if pedalboard == self.pedalboard and not force:
            return

        self._pedalboard = pedalboard
        self._device_controller.pedalboard = pedalboard
        self._save_current_pedalboard()

        if notify:
            self.app.components_observer.on_current_pedalboard_changed(self.pedalboard)

    @property
    def bank(self):
        """
        Get the :class:`.Bank` of the current :class:`.Pedalboard`
        """
        return self.pedalboard.bank if self.pedalboard is not None else None

    # ************************
    # Persistence
    # ************************
    def _load_current_pedalboard(self):
        data = self._dao.load()
        if not data.empty:
            bank, pedalboard = data.bank, data.pedalboard
            try:
                return self._manager.banks[bank].pedalboards[pedalboard]
            except IndexError:
                return None

        return None

    def _save_current_pedalboard(self):
        if self.pedalboard is None:
            self._dao.save_empty()
        else:
            bank_index = self.pedalboard.bank.index
            pedalboard_index = self.pedalboard.index

            self._dao.save(bank_index, pedalboard_index)

    # ************************
    # Set Current Pedalboard/Bank
    # ************************
    def to_before_pedalboard(self):
        """
        Change the current :class:`.Pedalboard` for the previous pedalboard.

        If the current pedalboard is the first in the current :class:`Bank`,
        the current pedalboard is will be the **last of the current Bank**.

        .. warning::

            If the current :attr:`.pedalboard` is ``None``, a :class:`.CurrentPedalboardError` is raised.
        """
        if self.pedalboard is None:
            raise CurrentPedalboardError('The current pedalboard is None')

        before_index = self.pedalboard.index - 1
        if before_index == -1:
            before_index = len(self.bank.pedalboards) - 1

        self.set_pedalboard(self.bank.pedalboards[before_index])

    def to_next_pedalboard(self):
        """
        Change the current :class:`.Pedalboard` for the next pedalboard.

        If the current pedalboard is the last in the current :class:`.Bank`,
        the current pedalboard is will be the **first of the current Bank**

        .. warning::

            If the current :attr:`.pedalboard` is ``None``, a :class:`.CurrentPedalboardError` is raised.
        """
        if self.pedalboard is None:
            raise CurrentPedalboardError('The current pedalboard is None')

        next_index = self.pedalboard.index + 1
        if next_index == len(self.bank.pedalboards):
            next_index = 0

        self.set_pedalboard(self.bank.pedalboards[next_index])

    def to_before_bank(self):
        """
        Change the current :class:`Bank` for the before bank. If the current
        bank is the first, the current bank is will be the last bank.

        The current pedalboard will be the first pedalboard of the new current bank
        **if it contains any pedalboard**, else will be ``None``.

        .. warning::

            If the current :attr:`.pedalboard` is ``None``, a :class:`.CurrentPedalboardError` is raised.
        """
        if self.pedalboard is None:
            raise CurrentPedalboardError('The current pedalboard is None')

        before_index = self.bank.index - 1
        if before_index == -1:
            before_index = len(self._manager.banks) - 1

        self.set_bank(self._manager.banks[before_index])

    def to_next_bank(self):
        """
        Change the current :class:`Bank` for the next bank. If the current
        bank is the last, the current bank is will be the first bank.

        The current pedalboard will be the first pedalboard of the new current bank
        **if it contains any pedalboard**, else will be ``None``.

        .. warning::

            If the current :attr:`.pedalboard` is ``None``, a :class:`.CurrentPedalboardError` is raised.
        """
        if self.pedalboard is None:
            raise CurrentPedalboardError('The current pedalboard is None')

        next_index = self.next_bank_index(self.bank.index)

        self.set_bank(self._manager.banks[next_index])

    def next_bank_index(self, current_index):
        next_index = current_index + 1
        if next_index == len(self._manager.banks):
            return 0

        return next_index

    def set_bank(self, bank, try_preserve_index=False):
        """
        Set the current :class:`Bank` for the bank
        only if the ``bank != current_bank``

        The current pedalboard will be the first pedalboard of the new current bank
        **if it contains any pedalboard**, else will be ``None``.

        .. warning::

            If the current :attr:`.pedalboard` is ``None``, a :class:`.CurrentPedalboardError` is raised.

        :param Bank bank: Bank that will be the current
        :param bool try_preserve_index: Tries to preserve the index of the current pedalboard
                                        when changing the bank. That is, if the current pedalboard is the fifth,
                                        when updating the bank, it will attempt to place the fifth pedalboard
                                        of the new bank as the current one. If it does not get
                                        (``len(bank.pedalboards) < 6``) the current pedalboard will be the
                                        first pedalboard.
        """
        if bank not in self._manager:
            raise CurrentPedalboardError('Bank {} has not added in banks manager'.format(bank))

        if self.bank == bank:
            return

        if bank.pedalboards:
            pedalboard = self._equivalent_pedalboard(bank) if try_preserve_index else bank.pedalboards[0]
            self.set_pedalboard(pedalboard)
        else:
            self.set_pedalboard(None)

    def _equivalent_pedalboard(self, other_bank):
        index = self.pedalboard.index
        try:
            return other_bank.pedalboards[index]
        except IndexError:
            return other_bank.pedalboards[0]
