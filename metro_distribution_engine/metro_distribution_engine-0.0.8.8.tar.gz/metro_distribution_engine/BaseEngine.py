from abc import ABC, abstractmethod

class BaseEngine(ABC):
    '''
        This is the abstraction representing an engine for data distribution.

        DistributionEngines must be able to create distribution channels for datasources
        and projects, connect those channels together, and send/receive data from either
        end of the system.
    '''

    @abstractmethod
    def create_datasource(self, datasource):
        pass

    @abstractmethod
    def attach(self, project, datasource):
        pass

    @abstractmethod
    def detach(self, subscription):
        pass

    @abstractmethod
    def send_metric(self, datasource_name, project_names, metric):
        # Might change
        pass

    @abstractmethod
    def get_metrics(self, metro_subscription):
        # Might change
        pass
