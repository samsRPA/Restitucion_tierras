from abc import ABC, abstractmethod


class IBrowserService(ABC):

    @abstractmethod
    async def scrapper_screenshots_notifications( self,city: str, court_office: str,current_year: str,litigando_court_id: int):
        pass
