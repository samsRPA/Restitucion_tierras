class TControlRep():
    def __init__(self, table):
        self._table = table
   
    async def addControlRecord(self, conn, litigandoCourtId, notificationId, ntfDate, pdfPages, csvRowCounts, oracleId,consecutive, origin):
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
                    :consecutive,
                    :pdfPages,
                    :csvRowCounts,
                    79961368,
                    :origin,
                    :oracleId,
                    sysdate
                )
            """
            async with conn.cursor() as cursor:
                await cursor.execute(query, {
                    "litigandoCourtId": litigandoCourtId,
                    "notificationId": notificationId,
                    "ntfDate": ntfDate,
                    "consecutive":consecutive,
                    "pdfPages": pdfPages,
                    "csvRowCounts": csvRowCounts,
                    "origin":origin,
                    "oracleId": oracleId
                })
                return True
        except Exception as e:
            raise RuntimeError(f"Error en insert de Control: {e}")