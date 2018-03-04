from sqlalchemy.ext.compiler import compiles

from .core import utcnow


@compiles(utcnow, 'sqlite')
def pg_utcnow(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"
