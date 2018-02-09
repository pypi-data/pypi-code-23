from schemapy.action import Action


def pydal_schema_actions_generator(api):
    for tablename in api.db.tables:
        table = api.db[tablename]

        @api.as_action(
            name='create_{0}'.format(tablename),
            type='create',
            request=[
                table[fieldname]
                for fieldname in table.fields
                if fieldname != 'id'
            ],
            response=table
        )
        def create(db, req, action):
            table = db[tablename]
            rowid = table.insert(**req)
            return [table[rowid]]

        @api.as_action(
            name='select_all_{0}'.format(tablename),
            type='read',
            response=table
        )
        def select(db, req, action):
            table = db[tablename]
            return db(table).select()

        @api.as_action(
            name='update_{0}'.format(tablename),
            type='update',
            request=table,
            response=table
        )
        def update(db, req, action):
            table = db[tablename]
            rowid = db(table.id == req.id).update(**req)
            return [table[rowid]]

        @api.as_action(
            name='delete_{0}'.format(tablename),
            type='delete',
            request=[table.id]
        )
        def delete(db, req, action):
            table = db[tablename]
            table[req.id].delete_record()
            return []


class API:
    def __init__(
        self,
        db,
        schema_actions_generator=pydal_schema_actions_generator,
    ):
        self.db = db
        self._actions = {}
        self._generator = schema_actions_generator

        self.define_actions_from_schema()

    def __del__(self):
        self.close()

    @property
    def actions(self):
        return list(self._actions.keys())

    def define_actions_from_schema(self):
        if self._generator is not None:
            self._generator(self)

    def __getattr__(self, attrname):
        try:
            attr = super().__getattr__(attrname)

        except AttributeError as err:
            try:
                attr = self._actions[attrname]

            except KeyError:
                raise err

        return attr

    def define_action(
        self,
        name,
        type='read',
        request=None,
        response=None,
        fn=None,
        **extras
    ):
        action = Action(
            self,
            name,
            type=type,
            request=request,
            response=response,
            fn=fn,
            **extras
        )
        self._actions[name] = action
        return action

    def as_action(
        self,
        type='read',
        request=None,
        response=None,
        **extras
    ):
        def decorator(fn):
            action = self.define_action(
                extras.pop('name', fn.__name__),
                type=type,
                request=request,
                response=response,
                fn=fn,
                **extras
            )

            def wrapper(**kwargs):
                return action(**kwargs)

            return wrapper

        return decorator

    def actionmethod(
        self,
        type='read',
        request=None,
        response=None,
        **extras
    ):
        def decorator(fn):
            action = Action(
                self,
                extras.pop('name', fn.__name__),
                type=type,
                request=request,
                response=response,
                fn=fn,
                ismethod=True,
                **extras
            )

            def wrapper(this, **kwargs):
                return action(this, **kwargs)

            return wrapper

        return decorator

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, errtype, err, tb):
        self.close()
