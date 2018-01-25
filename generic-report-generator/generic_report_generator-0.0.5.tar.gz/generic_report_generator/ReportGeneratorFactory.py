import importlib
from abc import ABC, abstractmethod

from sqlalchemy.engine import Engine
from sqlformat import ResultPersistenceStrategy

from .Error import SAEngineNotInitializedError, IncorrectInstanceTypeError
from .DropTempTableStrategy import DropTempTableStrategy
from .ResultDownloadStrategy import ResultDownloadStrategy

class ReportGeneratorFactory(ABC):
    sa_engine: Engine = None

    def create_sa_engine(self, connection_dialect, *args, **kwargs) -> Engine:
        self.sa_engine = self._create_sa_engine(connection_dialect, *args, **kwargs)
        return self.sa_engine

    @abstractmethod
    def _create_sa_engine(self, connection_dialect, *args, **kwargs) -> Engine:
        pass

    @abstractmethod
    def persistence_strategy(self, *args, **kwargs) -> ResultPersistenceStrategy:
        pass

    @abstractmethod
    def drop_all_temp_table_strategy(self, *args, **kwargs) -> DropTempTableStrategy:
        pass

    @abstractmethod
    def result_download_strategy(self, *args, **kwargs) -> ResultDownloadStrategy:
        pass

    def get_db_connection(self):
        if self.sa_engine is not None:
            return self.sa_engine.connect()
        else:
            raise SAEngineNotInitializedError("self.sa_engine is None")


def load_factory(factory_implement, *args, **kwargs) -> ReportGeneratorFactory:
    mod = ".".join(factory_implement.split('.')[0:-1])
    class_ = factory_implement.split('.')[-1]
    constructor = getattr(
        importlib.import_module(mod),
        class_
    )
    instance = constructor(*args, **kwargs)
    if isinstance(instance, ReportGeneratorFactory):
        return instance
    else:
        raise IncorrectInstanceTypeError("{} in not instance of ReportGeneratorFactory".format(factory_implement))
