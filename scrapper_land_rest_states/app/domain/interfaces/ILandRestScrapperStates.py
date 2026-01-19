
from abc import ABC, abstractmethod

class ILandRestScrapperStates(ABC):

    @abstractmethod
    async def scrapper(self,office):
        pass