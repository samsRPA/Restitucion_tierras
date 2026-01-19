import asyncio
from datetime import datetime
import logging


class LandRestRep:
    
    
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
        
    async def exists_control_estado(self, conn, despacho_id :int, codigo: str) -> bool:
        try:
            query = """
            SELECT 1
            FROM CONTROL_ESTADOS_RESTITUCION_TIERRAS
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



    # async def insert_TAWS(self, conn, hojas,consecutivo,registros,despacho_id,notificacion_id,correo):
    #     try:
    #         query = """
    #         INSERT INTO torre_archivos_aws (
    #             DESPACHO_ID,
    #             DESPACHO_JUDICIAL,
    #             CIUDAD,
    #             CODIGO,
    #             FECHA_CREACION_REGISTRO
    #         ) VALUES (
    #             :despacho_id,
    #             :despacho_judicial,
    #             :ciudad,
    #             :codigo,
    #             SYSDATE
    #         )
    #         """

    #         async with conn.cursor() as cursor:
    #             await cursor.execute(query, {
    #                 "despacho_id": despacho_id,
    #                 "despacho_judicial": despacho_judicial,
    #                 "ciudad": ciudad,
    #                 "codigo": codigo
    #             })
    #     except Exception as error:
    #         self.logger.error(f"❌ Error al insertar ek estado: {error}")
    #         raise


    async def update_fecha_visita(self, conn, despacho_judicial: str, codigo: str):
        query = """
        UPDATE CONTROL_ESTADOS_RESTITUCION_TIERRAS
        SET FECHA_ULTIMA_VISITA = SYSDATE
        WHERE DESPACHO_JUDICIAL = :despacho_judicial
          AND CODIGO = :codigo
        """

        async with conn.cursor() as cursor:
            await cursor.execute(query, {
                "despacho_judicial": despacho_judicial,
                "codigo": codigo
            })




   
    async def addControlRecord(self, conn, litigandoCourtId, notificationId, ntfDate, pdfPages, csvRowCounts, oracleId):
        try:
            query = f"""
                INSERT INTO {self._table} (
                    TORRE_ID,
                    DESPACHO_ID,
                    NOTIFICACION_ID,
                    FECHA_NOTIFICACION,
                    CONSECUTIVO,
                    CANT_PAGINAS,
                    CANT_PROCESOS,
                    FUNCIONARIO_ID,
                    ORIGEN,
                    ORACLE_ID,
                    FECHA_REGISTRO
                ) VALUES (
                    SQ_TORRE_CONTROL.NEXTVAL,
                    :litigandoCourtId,
                    :notificationId,
                    :ntfDate,
                    1,
                    :pdfPages,
                    :csvRowCounts,
                    79961368,
                    'Samai_auto',
                    :oracleId,
                    sysdate
                )
            """
            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "litigandoCourtId": litigandoCourtId,
                    "notificationId": notificationId,
                    "ntfDate": ntfDate,
                    "pdfPages": pdfPages,
                    "csvRowCounts": csvRowCounts,
                    "oracleId": oracleId
                })
                return True
        except Exception as e:
            raise RuntimeError(f"Error en insert de Control: {e}")
       
       
 
#Torre Aws

 

       
    async def getLastRecordDates(self, conn, litigandoCourtId: int, notificationId: int):
        try:
            query = f"""
                SELECT DISTINCT
                    FECHA_DOCUMENTO,
                    REGISTROS
                FROM
                    {self._table}
                WHERE
                    DESPACHO_ID = :litigandoCourtId
                AND
                    NOTIFICACION_ID = :notificationId
                AND
                    CORREO = 'Samai_auto'
                AND
                    ORIGEN = 'SAMAI'
                ORDER BY
                    FECHA_DOCUMENTO DESC
                FETCH FIRST 30 ROWS ONLY
            """
            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "litigandoCourtId": litigandoCourtId,
                    "notificationId": notificationId
                })
                rows = await cursor.fetchall()
                return rows
        except Exception as e:
            raise e
   
    async def getNextOracleId(self, conn) -> int:
        query = f"SELECT {self.seqAws}.NEXTVAL FROM dual"
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            row = await cursor.fetchone()
            return int(row[0])
       
    async def addAwsRecord(
        self, conn, oracleId:int, awsName:str,archivoAbby:str, pdfPages: int, csvRowCounts: int,
        litigandoCourtId: int, locationId: int, notificationId: int, ntfDate:datetime) -> int:
        try:
            query = f"""
                INSERT INTO {self._table} (
                    ORACLE_ID,
                    ARCHIVO_AWS_ORIGINAL,
                    ARCHIVO_AWS,
                    ARCHIVO_ABBY,
                    FECHA_CREACION,
                    HOJAS,
                    CONSECUTIVO,
                    REGISTROS,
                    DESPACHO_ID,
                    LOCALIDAD_ID,
                    NOTIFICACION_ID,
                    FECHA_DOCUMENTO,
                    CORREO,
                    ORIGEN
                ) VALUES (
                    :oracleId,
                    :awsNameOriginal,
                    :awsName,
                    :archivoAbby,
                    SYSDATE,
                    :pdfPages,
                    1,
                    :csvRowCounts,
                    :litigandoCourtId,
                    :locationId,
                    :notificationId,
                    :ntfDate,
                    'Samai_auto',
                    'SAMAI'
                )
            """
            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "oracleId": oracleId,
                    "awsNameOriginal":archivoAbby,
                    "awsName":awsName,
                    "archivoAbby": f"H:/BASE/SAMAI_PDF/{archivoAbby}",
                    "pdfPages": pdfPages,
                    "csvRowCounts": csvRowCounts,
                    "litigandoCourtId": litigandoCourtId,
                    "locationId": locationId,
                    "notificationId": notificationId,
                    "ntfDate":ntfDate
                })
                return True
        except Exception as e:
            raise RuntimeError(f"Error en insert de General: {e}")
 
 