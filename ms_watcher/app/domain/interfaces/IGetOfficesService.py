from abc import ABC, abstractmethod
 


class IGetOfficesService(ABC):


    @abstractmethod
    def get_offices(self):
        pass

