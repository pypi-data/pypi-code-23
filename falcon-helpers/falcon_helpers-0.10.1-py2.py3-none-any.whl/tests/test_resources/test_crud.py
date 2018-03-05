from datetime import timezone as tz
import pytest
import sqlalchemy as sa

import falcon
import falcon.testing
import marshmallow_sqlalchemy as ms

from falcon_helpers.resources.crud import CrudBase
from falcon_helpers.middlewares.sqla import SQLAlchemySessionMiddleware
from falcon_helpers.middlewares.marshmallow import MarshmallowMiddleware
from falcon_helpers.sqla.orm import BaseColumns, Testable, metadata
from falcon_helpers.sqla.db import session


engine = sa.create_engine('sqlite://')
Base = sa.ext.declarative.declarative_base(bind=engine)


class ModelOther(Base, BaseColumns, Testable):
    __tablename__ = 'mother'

    test_id = sa.Column(sa.Integer, sa.ForeignKey('mtest.id'), nullable=False)


class ModelTest(Base, BaseColumns, Testable):
    __tablename__ = 'mtest'

    name = sa.Column(sa.Unicode, nullable=False)
    other = sa.orm.relationship("ModelOther")


class ModelSchema(ms.ModelSchema):
    class Meta:
        model = ModelTest
        exclude = ('other',)


class BasicCrud(CrudBase):
    db_cls = ModelTest
    schema = ModelSchema


@pytest.fixture
def app():
    Base.metadata.drop_all()
    Base.metadata.create_all()

    app = falcon.API(
        middleware=[
            SQLAlchemySessionMiddleware(session),
            MarshmallowMiddleware(),
        ]
    )

    app.add_route('/crud/{obj_id}', BasicCrud())
    app.add_route('/bad', BasicCrud())
    return app


@pytest.fixture
def client(app):
    return falcon.testing.TestClient(app)


def test_crud_base_get_404_with_no_object(client):
    resp = client.simulate_get('/crud/1')
    assert resp.status_code == 404


def test_crud_base_get_500_with_misconfigured_route(client):
    resp = client.simulate_get('/bad')
    assert resp.status_code == 500


def test_crud_base_get_200_with_object(client):
    m1 = ModelTest.testing_create()
    session.add(m1)
    session.commit()
    resp = client.simulate_get(f'/crud/{m1.id}')

    assert resp.status_code == 200
    assert resp.json == {
        'id': m1.id,
        'name': m1.name,
        'created_ts': m1.created_ts.replace(tzinfo=tz.utc).isoformat(),
        'updated_ts': m1.updated_ts.replace(tzinfo=tz.utc).isoformat(),
    }


def test_crud_base_get_404_with_wrong_id(client):
    m1 = ModelTest.testing_create()
    session.add(m1)
    session.commit()
    resp = client.simulate_get(f'/crud/{m1.id + 1}')

    assert resp.status_code == 404


def test_crud_base_post(client):
    resp = client.simulate_post(
        f'/crud/new',
        json={
            'name': 'thing'
        })

    assert resp.status_code == 201
    assert session.query(ModelTest).get(resp.json['id']).name == 'thing'
    assert resp.json['name'] == 'thing'


def test_crud_base_delete(client):
    m1 = ModelTest.testing_create()
    session.add(m1)
    session.commit()

    resp = client.simulate_delete(f'/crud/{m1.id}')

    assert resp.status_code == 204
    assert session.query(ModelTest).get(m1.id) == None

def test_crud_base_delete_with_relationship(client):
    m1 = ModelTest.testing_create()
    session.add(m1)
    session.flush()

    mo1 = ModelOther.testing_create(test_id=m1.id)
    session.add(mo1)
    session.commit()

    resp = client.simulate_delete(f'/crud/{m1.id}')

    assert resp.status_code == 400
    assert session.query(ModelTest).get(m1.id) == m1
    assert session.query(ModelOther).get(mo1.id) == mo1

    assert 'errors' in resp.json
    assert resp.json['errors'] == ['Unable to delete because the object is connected to other objects']
