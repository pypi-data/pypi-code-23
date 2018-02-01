import pytest
from sqlalchemy import Column

from helper_slot_class import B
from piecash import Transaction
from piecash.kvp import DictWrapper, SlotInt, SlotGUID
from piecash.sa_extra import pure_slot_property, DeclarativeBase


class TestSlot_behavior(object):
    def test_pure_slot_property_int(self):
        class A(DictWrapper):
            slots = []
            prop = pure_slot_property('prop')

        a = A()
        assert len(a.slots) == 0
        assert a.prop is None

        # assignment of property
        a.prop = 4
        assert len(a.slots) == 1
        assert a.slots == [SlotInt(name="prop", value=4)]
        assert a.slots[0] != [SlotInt(name="prop", value=8)]
        assert a.slots[0] != [SlotInt(name="prop_notok", value=4)]
        assert a.prop == 4

