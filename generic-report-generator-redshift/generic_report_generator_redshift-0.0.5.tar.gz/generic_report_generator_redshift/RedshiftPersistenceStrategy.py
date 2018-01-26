from sqlformat import ResultPersistenceStrategy
from sqlformat.helper import sql_helper

from .model import RedshiftDBPersistent, AWSCredential


class RedshiftPersistenceStrategy(ResultPersistenceStrategy):
    def __init__(self, db_persistent: RedshiftDBPersistent, aws_credential: AWSCredential):
        super().__init__()
        self.db_persistent = db_persistent
        self.aws_credential = aws_credential


    def _init_buffer(self):
        return sql_helper.split_statements(self.db_persistent.get_init_buffer_sql())

    def _flush_buffer(self):
        return sql_helper.split_statements(
            self.db_persistent.get_flush_buffer_sql(
                self.aws_credential,
                self.buffer_destination
            )
        )

    @property
    def temp_table_name(self):
        return self.db_persistent.get_temp_table()

    def change_buffer_id(self):
        self.buffer_id = self.db_persistent.fixed_buffer_id

    @property
    def extra_procedure_variables(self):
        return {
            "__schema__": self.db_persistent.schema,
            "__temp_table__": self.temp_table_name
        }
