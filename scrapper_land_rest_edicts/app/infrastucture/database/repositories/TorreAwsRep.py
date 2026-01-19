#Torre Aws
from datetime import datetime
import logging
 
class TorreAwsRep():
    def __init__(self, table, seqAws):
        self.seqAws= seqAws
        self._table =table
        self.logger= logging.getLogger(__name__)
       
    async def notification_exists(self, conn, consecutive:int,records:int, litigandoCourtId:int,ntfDate:datetime, origin:str  ) -> bool:
        """
        Verifica si existe un documento en la tabla CONTROL_AUTOS_RAMA_1
        según la fecha_notificacion (DD-MM-YYYY), radicacion y consecutivo.
        """
        try:
            query = f"""
                SELECT 1
                FROM {self._table}
                WHERE FECHA_DOCUMENTO= :fecha_notificacion
                  AND CONSECUTIVO = :consecutive
                  AND  REGISTROS = :records
                  AND DESPACHO_ID = :litigandoCourtId
                  AND ORIGEN = :origin
                  FETCH FIRST 1 ROWS ONLY
                """
            async def _execute():
                async with conn.cursor() as cursor:
                    await cursor.execute(query, {
                        "fecha_notificacion": ntfDate,
                        "consecutive": consecutive,
                        "records":records,
                        "litigandoCourtId":litigandoCourtId,
                        "origin": origin   
                    })
                    row = await cursor.fetchone()
                    return row

            result = await _execute()
            return result is not None

        except Exception as error:
            self.logger.error(f"❌ Error en documento_existe: {error}")
            raise

    async def getNextOracleId(self, conn) -> int:
        query = f"SELECT {self.seqAws}.NEXTVAL FROM dual"
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            row = await cursor.fetchone()
            return int(row[0])
              
    async def addAwsRecord(
        self, conn, oracleId:int, awsName:str,archivoAbby:str, pdfPages: int, csvRowCounts: int,
        litigandoCourtId: int, locationId: int, notificationId: int, ntfDate:datetime,consecutive:int,origin:str ) -> int:
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
                    :consecutive,
                    :csvRowCounts,
                    :litigandoCourtId,
                    :locationId,
                    :notificationId,
                    :ntfDate,
                    'Restitucion_Node',
                    :origin
                )
            """
            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "oracleId": oracleId,
                    "awsNameOriginal":archivoAbby,
                    "awsName":awsName,
                    "archivoAbby": f"H:/BASE/SAMAI_PDF/{archivoAbby}",
                    "pdfPages": pdfPages,
                    "consecutive":consecutive,
                    "csvRowCounts": csvRowCounts,
                    "litigandoCourtId": litigandoCourtId,
                    "locationId": locationId,
                    "notificationId": notificationId,
                    "ntfDate":ntfDate,
                    "origin":origin
                })
                return True
        except Exception as e:
         
            raise RuntimeError(f"Error en insert de General: {e}")



    async def update_visit_date(self, conn, despacho_id: int, codigo: str):
        query = """
        UPDATE CONTROL_ESTADOS_RESTITUCION_TIERRAS
        SET FECHA_ULTIMA_VISITA = SYSDATE
        WHERE DESPACHO_ID = :DESPACHO_ID
          AND CODIGO = :codigo
        """

        async with conn.cursor() as cursor:
            await cursor.execute(query, {
                "DESPACHO_ID": despacho_id,
                "codigo": codigo
            })
