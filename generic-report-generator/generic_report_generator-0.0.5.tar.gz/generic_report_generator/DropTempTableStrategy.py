from abc import ABC, abstractmethod

class DropTempTableStrategy(ABC):
    def drop(self, connection):
        temp_tables = self.list_temp_table(connection)
        for temp_table in temp_tables:
            self.drop_temp_table(connection, temp_table)

    @abstractmethod
    def list_temp_table(self, connection):
        pass

    @abstractmethod
    def drop_temp_table(self, connection, temp_table):
        pass
