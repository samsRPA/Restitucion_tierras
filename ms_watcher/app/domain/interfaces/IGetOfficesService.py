from abc import ABC, abstractmethod
 


class IGetOfficesService(ABC):


    @abstractmethod
    def get_offices(self):
        pass

    async def insert_offices(self):
         pass 