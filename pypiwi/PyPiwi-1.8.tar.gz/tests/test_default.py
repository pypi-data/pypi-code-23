# -*- coding: utf-8 -*-
from io import StringIO
from os import path
from tempfile import mkdtemp

from pytest import raises

import pypiwi as p


def test_manager():
    tmpdir = mkdtemp()
    dbfile = path.join(tmpdir, 'test.db')

    manager = p.Manager(p.SqliteDatabase, dbfile)
    proxy = manager.proxy()

    class Base(p.Model):
        class Meta:
            database = proxy

    class Person(Base):
        first = p.CharField(max_length=50, default='', null=True)
        last = p.CharField(max_length=50, unique=True)
        birth = p.DateField(null=True)
        age = p.IntegerField(default=0, null=False)
        color = p.IntegerField(default=0)
        money = p.DecimalField(max_digits=5, decimal_places=2, null=True)

    class Notification(Base):
        person = p.ForeignKeyField(Person)
        message = p.TextField()

    assert manager.models == [Person, Notification]

    with raises(RuntimeError):
        proxy.initialize('dbfile')

    with manager.using():
        Person.create_table()
        Notification.create_table()

        assert Person.meta_database().database == manager.database_name
        assert Person.meta_name() == 'person'
        assert isinstance(Person.meta_fields(), dict)
        assert 'first' in Person.meta_fields()
        assert Person.meta_fields()['first'] is Person.meta_field('first')
        assert isinstance(Person.meta_field('first'), p.CharField)

        Person(first='Nils', last='Corver').save()

        assert [prs.first for prs in Person.select()] == ['Nils']
        assert Person.get_or_none(Person.first == 'Piet') is None

        person = Person.get(Person.first == 'Nils')
        person.last = 'Davids'
        person.save_dirty()

        with raises(Person.DoesNotExist):
            Person.get(Person.first == 'Piet')

        person = Person.from_dict({'first': 'Jones', 'last': 'James'})
        assert person.first == 'Jones'
        person.update_with({'last': 'Davids', 'ignore': 'me'},
                           exclude=['ignore'])
        assert person.to_dict() == {
            'id': None,
            'age': 0, 'birth': None, 'color': 0, 'money': None,
            'first': 'Jones', 'last': 'Davids'
        }

    analyser = manager.analyse()
    assert len(analyser.statements) == 0
    assert analyser.auto_migrate() is False

    class Person(p.Model):
        class Meta:
            database = proxy
            indexes = (
                (['first', 'last'], False),
            )

        first = p.CharField(max_length=50, default='', null=False)
        infix = p.CharField(default='')
        last = p.CharField(max_length=50, unique=False)
        age = p.IntegerField(default=0, null=True)
        color = p.CharField(default='red')
        money = p.DecimalField(max_digits=8, decimal_places=2, null=True)

    manager.models = [Person]

    class Role(Base):
        name = p.CharField()

    analyser.scan()

    writer = StringIO()
    analyser.print_migrations(out=writer)
    lines = [
        'notification = DroppableTable("notification")',
        'migrator.create_table(m.Role)',
        'migrator.add_column(m.Role, m.Role.name)',
        'migrator.drop_table(notification)',
        'migrator.drop_column(m.Person, p.Field(db_column="birth"))',
        'migrator.add_column(m.Person, m.Person.infix)',
        'migrator.add_not_null(m.Person, m.Person.first)',
        'migrator.drop_not_null(m.Person, m.Person.age)',
        'migrator.drop_index(m.person, ["last", ])',
        'migrator.add_index(m.Person, ["first", "last", ], False)',
    ]
    for line in lines:
        assert line in writer.getvalue()

    assert len(analyser.statements) == 9

    for statement in analyser.statements:
        item = statement[1]
        if isinstance(item, p.ComparableIndex):
            assert str(item)
        elif isinstance(item, p.ComparableField):
            assert str(item)

    analyser.print_migrations()
    analyser.auto_migrate()

    analyser.scan()
    assert len(analyser.statements) == 0

    with manager.using():
        assert [prs.infix for prs in Person.select()] == ['']

    class Role(Base):  # flake8: noqa
        name = p.CharField()
        will_not_work = p.CharField()

    manager.models = [Person, Role]

    analyser.scan()
    assert len(analyser.statements) == 1

    with raises(ValueError) as exc:
        analyser.auto_migrate()

    assert '`add_column`' in str(exc.value)
    assert '`role`.`will_not_work`' in str(exc.value)

    with manager.using():
        migrator = analyser.migrator

        migrator.drop_table(p.DroppableTable('role'))
