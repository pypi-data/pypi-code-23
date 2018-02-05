from schemapy import Action, ActionError
import pytest


class TestAction:
    def test_invalid_construct(self, api):
        with pytest.raises(ActionError):
            Action(api, 'foo', type='notcrud')

        with pytest.raises(ActionError):
            Action(api, 'foo', type='read')  # fn not callable

    def test_extra(self, api):
        a = Action(api, 'foo', type='read', fn=lambda *_: [], foo='bar')
        assert a.foo == 'bar'
