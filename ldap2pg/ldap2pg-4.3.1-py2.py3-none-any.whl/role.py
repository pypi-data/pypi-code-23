from __future__ import unicode_literals

from collections import OrderedDict
import logging

from .psql import Query
from .utils import unicode


logger = logging.getLogger(__name__)


class Role(object):
    def __init__(self, name, options=None, members=None, parents=None):
        self.name = name
        self.members = members or []
        self.options = RoleOptions(options or {})
        self.parents = parents or []

    def __eq__(self, other):
        return self.name == unicode(other)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return self.name

    def __lt__(self, other):
        return unicode(self) < unicode(other)

    @classmethod
    def from_row(cls, name, members, *row):
        self = Role(name=name, members=list(filter(None, members)))
        self.options.update_from_row(row)
        return self

    def create(self):
        yield Query(
            'Create %s.' % (self.name,),
            'postgres',
            'CREATE ROLE "%s" WITH %s;' % (self.name, self.options)
        )
        if self.members:
            yield Query(
                'Add %s members.' % (self.name,),
                'postgres',
                'GRANT "%(role)s" TO %(members)s;' % dict(
                    members=", ".join(map(lambda x: '"%s"' % x, self.members)),
                    role=self.name,
                ),
            )

    def alter(self, other):
        # Yields SQL queries to reach other state.

        if self.options != other.options:
            yield Query(
                'Update options of %s.' % (self.name,),
                'postgres',
                'ALTER ROLE "%s" WITH %s;' % (self.name, other.options),
            )

        if self.members != other.members:
            missing = set(other.members) - set(self.members)
            if missing:
                logger.debug(
                    "Role %s miss members %s.",
                    self.name, ', '.join(missing)
                )
                yield Query(
                    'Add missing %s members.' % (self.name,),
                    'postgres',
                    "GRANT \"%(role)s\" TO %(members)s;" % dict(
                        members=", ".join(map(lambda x: '"%s"' % x, missing)),
                        role=self.name,
                    ),
                )
            spurious = set(self.members) - set(other.members)
            if spurious:
                logger.debug(
                    "Role %s has spurious members %s.",
                    self.name, ', '.join(spurious)
                )
                yield Query(
                    'Delete spurious %s members.' % (self.name,),
                    'postgres',
                    "REVOKE \"%(role)s\" FROM %(members)s;" % dict(
                        members=", ".join(map(lambda x: '"%s"' % x, spurious)),
                        role=self.name,
                    ),
                )

    _drop_objects_sql = """
    REASSIGN OWNED BY "%(role)s" TO SESSION_USER;
    DROP OWNED BY "%(role)s";
    """.strip().replace(4 * ' ', '')

    def drop(self):
        yield Query(
            'Reassign %s objects and purge ACL on %%(dbname)s.' % (self.name,),
            Query.ALL_DATABASES,
            self._drop_objects_sql % dict(role=self.name),
        )
        yield Query(
            'Drop %s.' % (self.name,),
            'postgres',
            "DROP ROLE \"%(role)s\";" % dict(role=self.name),
        )

    def merge(self, other):
        self.members += other.members
        self.parents += other.parents
        return self


class RoleOptions(dict):
    COLUMNS = OrderedDict([
        # column: (option, default)
        ('rolbypassrls', ('BYPASSRLS', False)),
        ('rolcanlogin', ('LOGIN', False)),
        ('rolcreatedb', ('CREATEDB', False)),
        ('rolcreaterole', ('CREATEROLE', False)),
        ('rolinherit', ('INHERIT', True)),
        ('rolreplication', ('REPLICATION', False)),
        ('rolsuper', ('SUPERUSER', False)),
    ])

    SUPPORTED_COLUMNS = list(COLUMNS.keys())

    @classmethod
    def supported_options(cls):
        return [
            o for c, (o, _) in cls.COLUMNS.items()
            if c in cls.SUPPORTED_COLUMNS
        ]

    COLUMNS_QUERY = """
    SELECT array_agg(column_name::text)
    FROM information_schema.columns
    WHERE table_schema = 'pg_catalog' AND table_name = 'pg_authid'
    LIMIT 1
    """.replace('\n    ', '\n').strip()

    @classmethod
    def update_supported_columns(cls, columns):
        cls.SUPPORTED_COLUMNS = [
            c for c in RoleOptions.COLUMNS.keys()
            if c in columns
        ]
        logger.debug(
            "Postgres server supports role options %s.",
            ", ".join(cls.supported_options()),
        )

    def __init__(self, *a, **kw):
        defaults = dict([(o, d) for c, (o, d) in self.COLUMNS.items()])
        super(RoleOptions, self).__init__(**defaults)
        init = dict(*a, **kw)
        self.update(init)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return ' '.join((
            ('NO' if value is False else '') + name
            for name, value in self.items()
            if name in self.supported_options()
        ))

    def update_from_row(self, row):
        self.update(dict(zip(self.supported_options(), row)))

    def update(self, other):
        spurious_options = set(other.keys()) - set(self.keys())
        if spurious_options:
            message = "Unknown options %s" % (', '.join(spurious_options),)
            raise ValueError(message)
        return super(RoleOptions, self).update(other)


class RoleSet(set):
    def resolve_membership(self):
        index_ = self.reindex()
        for role in self:
            while role.parents:
                parent_name = role.parents.pop()
                parent = index_[parent_name]
                if role.name in parent.members:
                    continue
                logger.debug("Add %s as member of %s.", role.name, parent.name)
                parent.members.append(role.name)

    def reindex(self):
        return dict([(role.name, role) for role in self])

    def flatten(self):
        # Generates the flatten tree of roles, children first.

        index = self.reindex()
        seen = set()

        def walk(name):
            if name in seen:
                return
            try:
                role = index[name]
            except KeyError:
                # We are trying to walk a member out of set. This is the case
                # where a role is missing but not one of its member.
                return

            for member in role.members:
                for i in walk(member):
                    yield i
            yield name
            seen.add(name)

        for name in sorted(index.keys()):
            for i in walk(name):
                yield index[i]
