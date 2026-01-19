
from abc import ABC, abstractmethod

class ILandRestScrapperEdicts(ABC):

    @abstractmethod
    async def scrapper(self,office):
        pass