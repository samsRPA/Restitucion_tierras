import asyncio
import logging


class KeysLandRestitutionRepository:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)



    async def get_keys_offices(self, conn):
        try:

            
            #CONTROL_ESTADOS_RESTITUCION_TIERRAS  
            query = """
            select * from despachos_estados_restitucion  ERT
            inner join despachos d on d.despacho_id = ERT.despacho_id  
           
            """
#where ERT.despacho_id ='26893'
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall() 

            return rows 
        except Exception as error:
            self.logger.error(f"❌ Error al comprobar la existencia del estado: {error}")
            raise



