from schemapy import Action, ActionError, Response, ResponseError
import pytest


class TestAPI:
    def test_generation(self, api):
        assert 'create_foo' in api.actions
        assert 'select_all_foo' in api.actions
        assert 'update_foo' in api.actions
        assert 'delete_foo' in api.actions

    def test_getaction(self, api):
        assert isinstance(api.create_foo, Action)

        with pytest.raises(AttributeError):
            api.inexistant

    def test_action_validation(self, api):
        rows = api.create_foo(bar='hello')

        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'hello'
        assert rows[0].baz == 42

        with pytest.raises(ActionError):
            api.create_foo(baz=23)

        with pytest.raises(ActionError):
            api.create_foo(bar=42)

    def test_response_validation(self, api):
        @api.as_action(
            type='read',
            request=api.db.foo,
            response=api.db.foo
        )
        def valid_response(db, req, action):
            assert req.bar == 'hello'
            return {'bar': 'world'}

        @api.as_action(
            type='read',
            request=api.db.foo,
            response=api.db.foo
        )
        def invalid_response(db, req, action):
            assert req.bar == 'hello'
            return [
                {'bar': 'hello', 'baz': 'world'},
                {'baz': 42}
            ]

        rows = api.valid_response(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'world'

        rows = api.invalid_response(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 2

        with pytest.raises(ResponseError):
            rows[0]

        with pytest.raises(ResponseError):
            rows[1]

    def test_as_action(self, api):
        @api.as_action(
            type='read',
            request=api.db.foo,
            response=api.db.foo
        )
        def testfn(db, req, action):
            assert req.bar == 'hello'
            return {'bar': 'world'}

        assert 'testfn' in api.actions
        rows = testfn(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'world'

        rows = api.testfn(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'world'

    def test_cls(self, api):
        class TestClassAPI:
            def __init__(self):
                self.foo = 'bar'

            @api.actionmethod(
                type='read',
                request=api.db.foo,
                response=api.db.foo
            )
            def testmethod(self, db, req, action):
                assert self.foo == 'bar'
                assert req.bar == 'hello'
                return {'bar': 'world'}

        testobj = TestClassAPI()
        rows = testobj.testmethod(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'world'

    def test_crud(self, api):
        rows = api.create_foo(bar='hello')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'hello'

        rows = api.create_foo(bar='world')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'world'

        api.commit()

        rows = api.select_all_foo()
        assert isinstance(rows, Response)
        assert len(rows) == 2
        assert rows[0].bar == 'hello'
        assert rows[1].bar == 'world'

        records_id = [row.id for row in rows]

        rows = api.update_foo(id=records_id[0], bar='hello world')
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'hello world'

        rows = api.delete_foo(id=records_id[1])
        assert isinstance(rows, Response)
        assert len(rows) == 0

        rows = api.select_all_foo()
        assert isinstance(rows, Response)
        assert len(rows) == 1
        assert rows[0].bar == 'hello world'
