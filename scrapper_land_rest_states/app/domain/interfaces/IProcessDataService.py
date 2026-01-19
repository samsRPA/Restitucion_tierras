from abc import ABC, abstractmethod
from pathlib import Path

class IProcessDataService(ABC):

    @abstractmethod
    def generate_state_posting_pdf(self, notification: dict, output_path: str):
        pass

    @abstractmethod
    def generate_fijaciones_csv( self, fijaciones: list,  output_path: str): 
        pass
