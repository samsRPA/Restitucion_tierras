
from app.domain.interfaces.IGetDataService import IGetDataService
import logging
from app.application.dto.HoyPathsDto import HoyPathsDto
from app.domain.interfaces.IDataBase import IDataBase

from datetime import datetime
from app.domain.interfaces.IUploadDataService import IUploadDataService
from app.domain.interfaces.IBrowserService import IBrowserService
from app.domain.interfaces.ILandRestScrapperEdicts import ILandRestScrapperEdicts

class LandRestScrapperEdicts(ILandRestScrapperEdicts):

    def __init__(self,db: IDataBase, getData: IGetDataService,upload_data_service:IUploadDataService, browser_service:IBrowserService):
        self.db=db
        self.getData = getData
        self.upload_data_service=upload_data_service
        self.browser_service=browser_service
        self.logger= logging.getLogger(__name__)
  
    async def scrapper(self,office):
        conn=None
        try:
            conn = await self.db.acquire_connection()
            paths = HoyPathsDto.build().model_dump()
            litigando_court_id=office.litigando_court_id
            court_office=office.court_office
            city=office.city
            code=office.code
            current_year = str(datetime.now().year)
            self.logger.info( f"current_year: { current_year}")
            location_id=office.location_id
            notification_id=19
            pdf_pages=1
            origin="RESTITUCION_TIERRAS"

            #await self.browser_service.scrapper_screenshots_notifications(city,court_office,current_year,litigando_court_id)
            
            edicts = self.getData.get_edicts(code, current_year, court_office, city)
            self.logger.info( f"  Edictos: { edicts}")

            # ❌ ERROR / API FALLÓ
            if edicts is None:
                self.logger.warning(f"⚠️ Error consultando Edictos del despacho {court_office} "f"(id {litigando_court_id})" )
                return

            # 📭 SIN edicts
            if len(edicts) == 0:
                self.logger.info(f"📭 El despacho {court_office} (id {litigando_court_id}) " "NO tiene edictos ")
                return

                    # ✅ HAY edicts
            self.logger.info( f"📌 Hay {len(edicts)} edictos para el despacho "  f"{court_office} (id {litigando_court_id})")

            # if len(edicts) >= 1:
            #     await self.browser_service.scrapper_screenshots_notifications(city,court_office,current_year,litigando_court_id)
                
            for edict in edicts:
                result= await  self.upload_data_service.uploadData(conn, edict,code,court_office, city,location_id,litigando_court_id,notification_id, origin,pdf_pages)
                if not result:
                    continue
                
            # await self.db.commit(conn)
        except Exception as e:
            self.logger.error(f"❌ Error : {e}")
            raise e
        finally:
            if conn:
                try:
                    await self.db.release_connection(conn)
                except Exception as e:
                    self.logger.warning(f"Error liberando conexión DB: {e}")



