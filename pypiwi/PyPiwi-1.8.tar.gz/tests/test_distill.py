# -*- coding: utf-8 -*-
import datetime as dt
from os import path
from tempfile import mkdtemp

import pypiwi as p


def test_distill():
    tmpdir = mkdtemp()
    dbfile = path.join(tmpdir, 'test-distill.db')

    manager = p.Manager(p.SqliteDatabase, dbfile)
    proxy = manager.proxy()

    class Base(p.Model):
        class Meta:
            database = proxy

    class Company(Base):
        name = p.CharField()

    class Person(Base):
        first = p.CharField(max_length=50, default='', null=True)
        last = p.CharField(max_length=50, unique=True)

        company = p.ForeignKeyField(Company)

        @property
        def notifications(self):
            return (Notification.select()
                    .where(Notification.person == self))

    class Notification(Base):
        created = p.DateTimeField(default=dt.datetime.now)
        person = p.ForeignKeyField(Person)
        message = p.CharField()

    analyser = manager.analyse()
    analyser.scan()
    assert analyser.auto_migrate(), 'Auto-migration failed'

    with manager.using():
        c1 = Company()
        c1.name = 'Acme Inc.'
        c1.save()

        p1 = Person()
        p1.first = 'John'
        p1.last = 'Doe'
        p1.company = c1
        p1.save()

        Notification.create(person=p1, message='Account created.')
        Notification.create(person=p1, message='Login failed.')
        Notification.create(person=p1, message='Login succeeded.')

        p2 = Person()
        p2.first = 'Jane'
        p2.last = 'Doet'
        p2.company = c1
        p2.save()

        Notification.create(person=p2, message='Account created.')
        Notification.create(person=p2, message='Login succeeded.')

        cursor = (Person.select()
                  .order_by(Person.last.asc(),
                            Person.first.asc()))

        assert p.distill(cursor, [
            'id',
            'first',
            'notifications.message',
            'company.name',
        ]) == [{'company': {'name': 'Acme Inc.'},
                'first': 'John',
                'id': 1,
                'notifications': [{'message': 'Account created.'},
                                  {'message': 'Login failed.'},
                                  {'message': 'Login succeeded.'}]},
               {'company': {'name': 'Acme Inc.'},
                'first': 'Jane',
                'id': 2,
                'notifications': [{'message': 'Account created.'},
                                  {'message': 'Login succeeded.'}]}]
