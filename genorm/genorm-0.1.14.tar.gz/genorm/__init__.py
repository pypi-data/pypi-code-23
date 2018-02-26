"""

GenORM
~~~~~~

Simple functional MySQL/PostgreSQL ORM.
Designed for the **Entesoc** system but can be used anywhere.

Author:         Denis Khodus aka "Reagent"
License:        MIT

"""

from .manage import manager as orm
from .attributes import *
from .values import *
from .models import *
from .funcs import *
from .session import MysqlSession, PostgresqlSession
from .request import OrmSelectRequest, OrmUpdateRequest, OrmInsertRequest, OrmDeleteRequest, OrmUndeleteRequest
from .results import OrmRawResult, OrmResult
from .exceptions import *
from .utils import current_timestamp


__version__ = "0.1.14"


