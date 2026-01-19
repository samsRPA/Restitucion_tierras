from abc import ABC, abstractmethod
from pathlib import Path

class IGetDataService(ABC):
    
    @abstractmethod
    def get_report_dates_states(self, codigo: str,annio_actual, despacho_judicial, ciudad:str):
          pass


    @abstractmethod
    def get_state(self, codigo: str, key:str, id: int, despacho_judicial:str, ciudad:str):
        pass
