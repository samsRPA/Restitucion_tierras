from app.application.dto.ScrapperRequest import ScrapperRequest
from app.domain.interfaces.IScrapperService import IScrapperService
import logging

from app.domain.interfaces.ILandRestScrapperEdicts import ILandRestScrapperEdicts





class ScrapperService(IScrapperService):


  
    def __init__(self,body: ScrapperRequest,land_rest_scrapper_edicts:ILandRestScrapperEdicts):
        self.body = body
        self.land_rest_scrapper_edicts=land_rest_scrapper_edicts
        self.logger= logging.getLogger(__name__)

    async def runScrapper(self):
   
        try:
            # Construir el DTO que espera run_multi
            office= ScrapperRequest(
                litigando_court_id=self.body.litigando_court_id,
                court_office=self.body.court_office,
                city=self.body.city,
                code=self.body.code,
                location_id=self.body.location_id
            )
            
            await self.land_rest_scrapper_edicts.scrapper(office)

        except Exception as e:
            self.logger.error(f"❌ Error : {e}")
            raise e
       
