import asyncio
import logging


class KeysLandRestitutionRepository:
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def exists_control_estado(self, conn, despacho_id :int, codigo: str) -> bool:
        try:
            query = """
            SELECT 1
            FROM despachos_estados_restitucion
            WHERE DESPACHO_ID = :despacho_id
            AND CODIGO = :codigo
            """

            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "despacho_id": despacho_id,
                    "codigo": codigo
                })
                row = await cursor.fetchone()

            return row is not None
        except Exception as error:
            self.logger.error(f"❌ Error al comprobar la existencia del estado: {error}")
            raise

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


    async def insert_control_estado(self, conn, despacho_id, despacho_judicial, ciudad, codigo):
        try:
            query = """
            INSERT INTO despachos_estados_restitucion(
                DESPACHO_ID,
                DESPACHO_JUDICIAL,
                CIUDAD,
                CODIGO,
                FECHA_CREACION_REGISTRO
            ) VALUES (
                :despacho_id,
                :despacho_judicial,
                :ciudad,
                :codigo,
                SYSDATE
            )
            """

            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "despacho_id": despacho_id,
                    "despacho_judicial": despacho_judicial,
                    "ciudad": ciudad,
                    "codigo": codigo
                })
        except Exception as error:
            self.logger.error(f"❌ Error al insertar ek estado: {error}")
            raise


