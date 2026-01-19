from abc import ABC, abstractmethod

class IUploadDataService(ABC):

    @abstractmethod
    async def uploadData(self,conn, state,code,court_office, city,location_id,litigando_court_id,notification_id, origin,pdf_pages):
        pass
