from io import StringIO

from .exceptions import InsertError, UpdateError, DeleteError
from .sql.dml import Insert, Update, Delete

class InsertBuilder(object):
    def __init__(self, table, columns=[], db=None):
        if db is None:
            raise InsertError('Attempting to build an insert statement without a database.')
        
        self._db = db
        self._table = table
        self._column_names = []
        self.add_columns(*columns)
    
    def add_columns(self, *columns):
        """Adds all columns in the arguments to the insert statement.
        
        :param columns: All arguments provided to the method.
          Column names as strings and `Column` objects are accepted.
        
        :return: `self` for method chaining.
        """
        for column in columns:
            if isinstance(column, str):
                column_name = column
            else:
                column_name = column.name
            
            self._table.columns[column_name] # Should raise exception if no column with name exists in table
            self._column_names.append(column_name)
        
        return self
    
    def get(self):
        return Insert(self._construct_sql(), self._table, self._column_names, db=self._db)
    
    def _construct_sql(self):
        return 'INSERT INTO {0} ({1})'.format(
            self._table.name,
            ','.join(self._column_names)
        )

class UpdateBuilder(object):
    def __init__(self, table, db=None):
        if db is None:
            raise UpdateError('Attempting to build an update statement without a database.')
        
        self._db = db
        self._table = table
        self._updates = []
        self._conditions = []
    
    def get(self):
        statement, params = self._construct_sql()
        return Update(statement, params, self._db)
    
    def set_(self, column, value):
        """Adds a column-value pair to the update statement.
        
        :param column: A column in the table to set to a value.
            Column names as strings and `Column` objects are accepted.
        :param value: An expression to set the column value to.
        
        :return: `self` for method chaining.
        """
        if isinstance(column, str):
            column = self._table.columns[column]
        
        self._updates.append((column, value))
        
        return self
    
    def where(self, *conditions):
        """Adds filtering conditions to the rows to update.
        
        :param conditions: The expressions to filter with.
        
        :return: `self` for method chaining.
        """
        self._conditions.extend(conditions)
        
        return self
    
    def _construct_sql(self):
        statement_buffer = StringIO()
        params = []
        
        statement_buffer.write('UPDATE {} SET\n\t'.format(self._table.name))
        
        statement_buffer.write(',\n\t'.join(
            '{0} = {1}'.format(u[0].name, u[1]._get_ref_field())
            for u in self._updates
        ))
        for update in self._updates:
            params.extend(update[0]._get_params())
            params.extend(update[1]._get_params())
        
        if len(self._conditions) > 0:
            statement_buffer.write('\nWHERE ')
            
            statement_buffer.write('\n  AND '.join(
                cond._get_ref_field() for cond in self._conditions))
            for cond in self._conditions:
                params.extend(cond._get_params())
        
        return (statement_buffer.getvalue(), params)

class DeleteBuilder(object):
    def __init__(self, table, db=None):
        if db is None:
            raise DeleteError('Attemping to build a delete statement without a database.')
        
        self._db = db
        self._table = table
        self._conditions = []
    
    def get(self):
        statement, params = self._construct_sql()
        return Delete(statement, params, self._db)
    
    def where(self, *conditions):
        """Adds filtering conditions to the rows to delete.
        
        :param conditions: The expression to filter with.
        
        :return: `self` for method chaining.
        """
        self._conditions.extend(conditions)
        
        return self
    
    def _construct_sql(self):
        statement_buffer = StringIO()
        params = []
        
        statement_buffer.write('DELETE FROM {}'.format(self._table.name))
        
        if len(self._conditions) > 0:
            statement_buffer.write('\nWHERE ')
            
            statement_buffer.write('\n  AND '.join(
                cond._get_ref_field() for cond in self._conditions))
            for cond in self._conditions:
                params.extend(cond._get_params())
        
        return (statement_buffer.getvalue(), params)
