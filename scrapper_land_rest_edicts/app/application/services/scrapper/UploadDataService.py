

from datetime import datetime
import logging
from pathlib import Path

import requests
from app.domain.interfaces.IUploadDataService import IUploadDataService
import os
from app.domain.interfaces.IGetDataService import IGetDataService
from app.domain.interfaces.IProcessDataService import IProcessDataService
import logging
from datetime import datetime
from app.infrastucture.database.repositories import TControlRep, TorreAwsRep
from app.domain.interfaces.IS3Manager import IS3Manager

import os
import subprocess
import requests
from pathlib import Path
from datetime import datetime
class UploadDataService(IUploadDataService):
    
    logger= logging.getLogger(__name__)
    
    def __init__(self,torreAwsRep:TorreAwsRep, tControlRep:TControlRep, getData: IGetDataService, processData: IProcessDataService, S3_manager:IS3Manager):
    
        self.torreAwsRep=torreAwsRep
        self.tControlRep=tControlRep
        self.getData = getData
        self.processData = processData
        self.S3_manager = S3_manager
        self.logger= logging.getLogger(__name__)
  



    async def uploadData(self,conn, edict, code,court_office, city,location_id,litigando_court_id,notification_id, origin,pdf_pages):
        try:
            process_code = edict.get("codProceso")
            property_name = edict.get("predio")
            property_municipality = edict.get("municipioPredio")

            start_date = edict.get("fechaInicio")
            end_date = edict.get("fechaFin")

            hash_value = edict.get("hash")
            code = edict.get("codigo")

            # Nested object
            link_doc = edict.get("linkDoc", {})
            link_name = link_doc.get("nombre")
            link_url = link_doc.get("url")
            link_tracker = link_doc.get("tracker")

            
            # #notification = self.getData.get_edict(code, edict_key,  edict_id, court_office, city,)
            # fijaciones = notification.get("fijacionEstado", [])    
            # ntfDate_str = notification.get("fechaEstado", "")
            # consecutive = notification.get("consecutivo", "") 
            # total_registrations = len(fijaciones)
                    
            ntfDate_dt = None
            if start_date:
                try:
                    ntfDate_dt = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    self.logger.warning(f"⚠️ Fecha inválida recibida: {start_date}")
                    return False
                                       
            
            oracleId = await  self.torreAwsRep.getNextOracleId(conn)
            self.logger.info( f"  oracleId: { oracleId}")
                            #Crear nombre
            fileName = f"{ntfDate_dt.strftime('%Y_%m%d')}_Samai_{location_id}_{litigando_court_id}_{notification_id}_{oracleId}_0_{court_office}_EDICTO"
            self.logger.info( f" filename: {fileName}")
            awsName = f"SCAN_{ntfDate_dt.strftime('%Y%m%d')}_Samai_{oracleId}.pdf"   
            self.logger.info( f"  awsName: {awsName}")
                    #pdf=f"{court_office}_{litigando_court_id}_{ ntfDate_fmt}_{consecutivo}_1_{total_registrations}.pdf"
            path=f"/app/output/pdfs/{fileName}.pdf"



            pdf_path = await self.download_and_convert_edict(
                link_url=link_url,
                file_name=fileName
            )

            if not pdf_path:
                self.logger.warning("⚠️ No se pudo generar el PDF del edicto")
                return False

            self.logger.info(f"📂 PDF final listo: {pdf_path}")


            #notification_exists= await self.torreAwsRep.notification_exists( conn, consecutive,total_registrations , litigando_court_id, ntfDate_dt, origin)

            # if notification_exists:
            #     self.logger.info(f"📂 [{edict_id}] Notificacion  ya existe en la BD (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}). No se insertará.")
            #     return False 
                

            # self.logger.info("📄 Generando PDF de fijación de estado")
            # pdf_hash= self.processData.generate_edict_posting_pdf( notification, output_path=path)
                    
            # if os.path.exists(path):
            #     its_uploades_s3= self.S3_manager.uploadFile(path)

            #     if its_uploades_s3:
            #         self.logger.info(f"✅ archivo  {path} subido a S3")
            #                 #fecha_db = ntfDate_dt.strftime('%d/%m/%Y')
            #                 #self.logger.info( f" filename: { fecha_db}")
            #             #Insertar registro en torre aws y torre
            #         inserted_taws= await self.torreAwsRep.addAwsRecord( conn, oracleId, awsName, f"{fileName}.pdf", pdf_pages,
            #                     total_registrations, litigando_court_id, location_id, notification_id,ntfDate_dt,consecutive,origin)

            #         if inserted_taws:
            #             self.logger.info(f"🟢 Notificacion insertada en TAWS (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}).")

            #         inserted_ta=await self.tControlRep.addControlRecord( conn, litigando_court_id,notification_id,ntfDate_dt ,   pdf_pages, total_registrations, oracleId,consecutive, origin)

            #         if inserted_taws:
            #             self.logger.info(f"🔵 Notificacion insertada en TA (consecutivo ={consecutive}, fecha={ntfDate_dt}, despacho id={litigando_court_id}).")

            #         # try:
            #         #     time.sleep(5)
            #         #     os.remove(path)
            #         #     self.logger.info(f"🗑️ Archivo local eliminado: {path}")
            #         # except Exception as e:
            #         #     self.logger.error(f"⚠️ No se pudo eliminar el archivo local {path}: {e}")
            #         #     return False
            #     else:
            #         self.logger.warning(f"⚠️ Error al subir {path} a S3, se mantiene local.")  
            #         return False
                                
            # else:
            #     self.logger.warning(f"⚠️ Archivo renombrado no encontrado: {path} – No se sube a S3.")
            #     return False

                            
            # csv_path = ( f"output/csv/" f"{ fileName}.csv")

            # self.processData.generate_fijaciones_csv(fijaciones=fijaciones, output_path=csv_path)  
            # self.S3_manager.uploadFile(csv_path)
            return True   
        except Exception as e:
            self.logger.warning(f"Error al subir la data a s3 y BD {e}")
            return False




    async def download_and_convert_edict(
        self,
        link_url: str,
        file_name: str
    ) -> str | None:
        """
        Descarga el documento del endpoint de edictos.
        - Si es PDF: lo guarda directamente
        - Si es Word (doc/docx): lo convierte a PDF
        Retorna la ruta final del PDF o None si falla
        """

        output_dir = Path("output/pdfs/edictos")
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"🌐 Descargando edicto desde: {link_url}")
            response = requests.get(link_url, timeout=60)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").lower()

            # =========================
            # Detectar tipo de archivo
            # =========================
            if "pdf" in content_type:
                pdf_path = output_dir / f"{file_name}.pdf"

                with open(pdf_path, "wb") as f:
                    f.write(response.content)

                self.logger.info(f"✅ PDF guardado: {pdf_path}")
                return str(pdf_path)

            elif "word" in content_type or "officedocument" in content_type:
                word_path = output_dir / f"{file_name}.docx"

                with open(word_path, "wb") as f:
                    f.write(response.content)

                self.logger.info(f"📄 Word descargado: {word_path}")
                pdf_path = self._convert_word_to_pdf(word_path, output_dir)

                return pdf_path

            else:
                self.logger.warning(
                    f"⚠️ Tipo de archivo no soportado: {content_type}"
                )
                return None

        except Exception as e:
            self.logger.error(f"❌ Error descargando edicto: {e}")
            return None

    def _convert_word_to_pdf(self, word_path: Path, output_dir: Path) -> str | None:
        """
        Convierte un archivo Word a PDF usando LibreOffice
        """

        try:
            self.logger.info("🔄 Convirtiendo Word a PDF (LibreOffice)")

            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(output_dir),
                    str(word_path)
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            pdf_path = output_dir / f"{word_path.stem}.pdf"

            if pdf_path.exists():
                self.logger.info(f"✅ Conversión exitosa: {pdf_path}")
                return str(pdf_path)

            self.logger.error("❌ No se generó el PDF")
            return None

        except Exception as e:
            self.logger.error(f"❌ Error convirtiendo Word a PDF: {e}")
            return None
