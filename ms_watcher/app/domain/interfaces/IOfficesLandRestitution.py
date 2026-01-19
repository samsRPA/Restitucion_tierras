from abc import ABC, abstractmethod


class IOfficesLandRestitution(ABC):



    @abstractmethod
    async def publish_offices(self):
        pass