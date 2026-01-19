

from app.domain.interfaces.IGetOfficesService import IGetOfficesService

import logging
from app.domain.interfaces.IRabbitMQProducer import IRabbitMQProducer

from app.domain.interfaces.IOfficesLandRestitution import IOfficesLandRestitution
class OfficesLandRestitution(IOfficesLandRestitution):

    logger= logging.getLogger(__name__)
   
    def __init__(self,  getData:IGetOfficesService, producer: IRabbitMQProducer):
        self.getData = getData
        self.producer= producer
     
    async def getAllOffices(self):
      
        try:
            
            #raw_offices = await self.getData.get_offices()
            raw_offices =  await self.getData.get_offices()
            if raw_offices:
                self.logger.info(f"✅ Se extrayeron {len(raw_offices)} despachos")
            return raw_offices
        except Exception as e:
            self.logger.error(f"❌ Error : {e}")
            raise e
 

    async def publish_offices(self):
   
            try:
                
                #await self.getData.insert_offices()
                offices= await self.getAllOffices()

                if not offices:
                    raise ValueError("No hay despachos para publicar")
                
                for office in offices:
                    print(office)
    
                    await self.producer.publishMessage(office.dict())
                    
 
            except Exception as error:
                logging.exception(f"Error al publicar {error}")
                raise error 
       
    
