from abc import ABC, abstractmethod

class ResultDownloadStrategy(ABC):

    @abstractmethod
    def download(self, download_from, csv_header):
        pass
