import sqlalchemy as sa
import falcon

from ..utils import flatten


class ListBase:
    """A base class for returning list of objects.

    This base class assumes you are using the marshmallow middleware for object
    serialization and sqlalchemy for database access.

    Attributes:
        db_cls: Set this to a SQLAlchemy entity
        schema: Set this a Marshmallow schema
    """
    db_cls = None
    schema = None

    default_order = None

    def on_get(self, req, resp):
        result = self.get_objects(req)
        schema = self.schema(many=True)

        resp.status = falcon.HTTP_200
        resp.body = schema.dump(result)

    def base_query(self):
        return self.session.query(self.db_cls)

    def pagination_hook(self, query, req):
        """Create a hook for pagination"""
        size = int(req.params.get('pageSize', 50))

        # -1 here is so that the page numbers start at 1
        page = int(req.params.get('page', 1)) - 1

        if page < 0:
            page = 0

        return query.limit(size).offset((page * size))

    def filter_hook(self, query, req):
        return query

    def order_hook(self, query, req):
        request_order = req.params.get('sort_by', [])

        # This takes advantage of falcons duplicate-param parsing which returns
        # a list when it finds a param multiple times.
        if type(request_order) != list:
            request_order = [request_order]

        request_order = list(flatten([x.split(';') for x in request_order]))
        request_order = [sa.desc(x[1:]) if x.startswith('-') else sa.asc(x) for x in request_order ]

        default_order = request_order or self.default_order or self.db_cls.__mapper__.primary_key
        return query.order_by(*default_order)

    def get_objects(self, req):
        base = self.base_query()
        order = self.order_hook(base, req)
        paged = self.pagination_hook(order, req)

        return paged.all()


class CrudBase:
    """A very simple CRUD resource.

    This base class assumes you are using the marshmallow middleware for object
    serialization and sqlalchemy for database access.

    Attributes:
        db_cls: Set this to a SQLAlchemy entity
        schema: Set this a Marshmallow schema
    """
    db_cls = None
    schema = None

    def on_get(self, req, resp, obj_id):
        result = self.session.query(self.db_cls).get(obj_id)

        if not result:
            raise falcon.HTTP_404

        schema = self.schema()
        resp.status = falcon.HTTP_200
        resp.body = schema.dump(result)


    def on_put(self, req, resp, obj_id):
        self.session.add(req.context['dto'].data)
        self.session.flush()

        resp.status = falcon.HTTP_200
        resp.body = self.schema().dump(req.context['dto'].data)


    def on_post(self, req, resp, obj_id):
        self.session.add(req.context['dto'].data)
        self.session.flush()

        resp.status = falcon.HTTP_201
        resp.body = self.schema().dump(req.context['dto'].data)


    def on_delete(self, req, resp, obj_id):
        try:
            result = (self.session
                     .query(self.db_cls)
                     .filter_by(id=obj_id)
                     .delete(synchronize_session=False))
        except sa.exc.IntegrityError:
            self.session.rollback()
            resp.status = falcon.HTTP_400
            resp.json = {'errors': [('Unable to delete because the object is '
                                    'connected to other objects')]}
        else:
            resp.status = falcon.HTTP_204
