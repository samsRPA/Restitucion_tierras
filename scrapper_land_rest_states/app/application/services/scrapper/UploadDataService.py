

from datetime import datetime
import logging
from pathlib import Path
import time
from app.domain.interfaces.IUploadDataService import IUploadDataService
import os
from app.domain.interfaces.IGetDataService import IGetDataService
from app.domain.interfaces.IProcessDataService import IProcessDataService
import logging
from datetime import datetime
from app.infrastucture.database.repositories import TControlRep, TorreAwsRep
from app.domain.interfaces.IS3Manager import IS3Manager


class UploadDataService(IUploadDataService):
    
    logger= logging.getLogger(__name__)
    
    def __init__(self,torreAwsRep:TorreAwsRep, tControlRep:TControlRep, getData: IGetDataService, processData: IProcessDataService, S3_manager:IS3Manager):
    
        self.torreAwsRep=torreAwsRep
        self.tControlRep=tControlRep
        self.getData = getData
        self.processData = processData
        self.S3_manager = S3_manager
        self.logger= logging.getLogger(__name__)
  



    async def uploadData(self,conn, state,code,court_office, city,location_id,litigando_court_id,notification_id, origin,pdf_pages):
        try:
            state_id = state.get("id")
            state_key = state.get("key")          
            notification = self.getData.get_state(code, state_key,  state_id, court_office, city,)
            fijaciones = notification.get("fijacionEstado", [])    
            ntfDate_str = notification.get("fechaEstado", "")
            consecutive = notification.get("consecutivo", "") 
            total_registrations = len(fijaciones)
                    
            ntfDate_dt = None
            if ntfDate_str:
                try:
                    ntfDate_dt = datetime.strptime(ntfDate_str, "%Y-%m-%d")
                except ValueError:
                    self.logger.warning(f"⚠️ Fecha inválida recibida: {ntfDate_str}")
                    return False                             
          
            oracleId = await  self.torreAwsRep.getNextOracleId(conn)
          
                            #Crear nombre
            fileName = f"{ntfDate_dt.strftime('%Y_%m%d')}_Tierras_{location_id}_{litigando_court_id}_{notification_id}_{oracleId}_0_{court_office}_ESTADO"
           
            awsName = f"SCAN_{ntfDate_dt.strftime('%Y%m%d')}_Tierras_{oracleId}.pdf"   
         
                    #pdf=f"{court_office}_{litigando_court_id}_{ ntfDate_fmt}_{consecutivo}_1_{total_registrations}.pdf"
            path = Path("/app/output/pdfs") / f"{fileName}.pdf"


            notification_exists= await self.torreAwsRep.notification_exists( conn, consecutive,total_registrations , litigando_court_id, ntfDate_dt, origin)

            if notification_exists:
                self.logger.info(f"📂 [{state_id}] Notificacion  ya existe en la BD (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}). No se insertará.")
                return False 
                

            self.logger.info("📄 Generando PDF de fijación de estado")
            pdf_hash= self.processData.generate_state_posting_pdf( notification, output_path=path)
                    
            if not path.exists():
                self.logger.warning(
                f"⚠️ Archivo renombrado no encontrado: {path} – No se sube a S3."
                )
                return False
        
            its_uploades_s3= self.S3_manager.uploadFile(str(path))

            if not its_uploades_s3:
                self.logger.warning(f"⚠️ Error al subir {path} a S3, ")
                return False

                
            self.logger.info(f"✅ archivo  {str(path)} subido a S3")
                            #fecha_db = ntfDate_dt.strftime('%d/%m/%Y')
                            #self.logger.info( f" filename: { fecha_db}")
                        #Insertar registro en torre aws y torre
            inserted_taws= await self.torreAwsRep.addAwsRecord( conn, oracleId, awsName, f"{fileName}.pdf", pdf_pages,total_registrations, litigando_court_id, location_id, notification_id,ntfDate_dt,consecutive,origin)

            if inserted_taws:
                self.logger.info(f"🟢 Notificacion insertada en TAWS (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}).")

            inserted_ta=await self.tControlRep.addControlRecord( conn, litigando_court_id,notification_id,ntfDate_dt ,   pdf_pages, total_registrations, oracleId,consecutive, origin)

            if inserted_taws:
                self.logger.info(f"🔵 Notificacion insertada en TA (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}).")

                try:
                    time.sleep(5)
                    os.remove(path)
                    self.logger.info(f"🗑️ Archivo local eliminado: {path}")
                except Exception as e:
                    self.logger.error(f"⚠️ No se pudo eliminar el archivo local {path}: {e}")
                    return False
                           
            csv_path = Path("app/output/csv") / f"{fileName}.csv"
            self.processData.generate_fijaciones_csv(fijaciones=fijaciones, output_path=csv_path) 
            
            if not csv_path.exists():
                self.logger.warning(f"⚠️ CSV no generado: {csv_path}")
                return False
          
            its_uploades_s3_csv=self.S3_manager.uploadFile(str(csv_path))
                
            if its_uploades_s3_csv:
                try:
                    time.sleep(5)
                    os.remove(csv_path)
                    self.logger.info(f"🗑️ Archivo local eliminado: {path}")
                except Exception as e:
                    self.logger.error(f"⚠️ No se pudo eliminar el archivo local {path}: {e}")
                    return False
                
            await self.torreAwsRep.update_visit_date( conn, litigando_court_id, code)
            return True   
        except Exception as e:
            self.logger.warning(f"Error al subir la data a s3 y BD {e}")
            return False