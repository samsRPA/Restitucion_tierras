from pathlib import Path
import pandas as pd
import logging

import json

from app.domain.interfaces.IDataBase import IDataBase

from app.domain.interfaces.IGetOfficesService import IGetOfficesService
from app.application.dto.OfficeDto import OfficeDto
from app.infrastucture.database.repositories.KeysLandRestitutionRepository import KeysLandRestitutionRepository

class GetOfficesService(IGetOfficesService):

    

    def __init__(self,db:IDataBase,repository:KeysLandRestitutionRepository):
        self.db = db
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def get_offices(self):
        conn = None
        try:
            conn = await self.db.acquire_connection()
            raw_keys = await self.repository.get_keys_offices( conn) 
            if not raw_keys:
                self.logger.warning("⚠️ No se encontraron despachos")
                return []
            offices_list = []

            for row in raw_keys:
                # row = (PROCESO_ID, INSTANCIA_RADICACION, ..., DEMANDADO)

        
                despacho_id = row[0]
                despacho_judicial = self._clean(row[1])
                ciudad = self._clean(row[2])
                codigo = self._clean(row[3])
                localidad_id= row[8]

 

                dto = OfficeDto(
                    litigando_court_id= despacho_id,
                    court_office = despacho_judicial,
                    city= ciudad,
                    code= codigo ,
                     location_id=localidad_id
                )
                offices_list.append(dto)
                 # Guardar JSON
                 
            json_ready = [dto.model_dump() for dto in offices_list]
            with open("/app/output/base/offices.json", "w", encoding="utf-8") as f:
                json.dump(json_ready, f, ensure_ascii=False, indent=4)

            return offices_list

    

        finally:
            if conn:
                await self.db.release_connection(conn)

            
        
        
    async def insert_offices(self): 
        conn = None
        try:
            conn = await self.db.acquire_connection()
            PROJECT_ROOT = Path(__file__).resolve().parents[4] 
            excel_path = PROJECT_ROOT / "output" / "base" / "LLAVES RESTITUCION DE TIERRAS - SCRAPPER.xlsx"
            df = pd.read_excel(excel_path)


            # Normalizar columnas
            df.columns = df.columns.str.strip().str.upper()

        

            for _, row in df.iterrows():

                # Campos tolerantes a fallo → si no existe la columna, devuelve ""
                despacho_id = row.get("DESPACHO_ID", "")
                despacho_judicial = self._clean(row.get("DESPACHO_JUDICIAL", ""))
                ciudad = self._clean(row.get("CIUDAD", ""))
                codigo = self._clean(row.get("CODIGO", ""))


                exists = await self.repository.exists_control_estado(
                    conn,
                    despacho_id,
                    codigo
                )
               
                if exists:
                    self.logger.info(
                        f"🔄 Ya existe  | "
                        f"{despacho_judicial} | {codigo} | {despacho_id}"
                    )
                    continue
            
              

              
                self.logger.info( f"➕ Insertando nuevo despacho | "
                        f"{despacho_judicial} | {codigo} | {despacho_id} "
                    )

                await self.repository.insert_control_estado(
                        conn,
                        despacho_id,
                        despacho_judicial,
                        ciudad,
                        codigo
                    )

           

                
            await conn.commit()
            # Guardar JSON
       

        except Exception as error:
            self.logger.exception(f"Error al procesar Excel: {error}")
            raise
        finally:
             if conn:
                await self.db.release_connection(conn)



    def _clean(self, value):
        # Si llega una Serie → tomar primer elemento
        if isinstance(value, pd.Series):
            value = value.iloc[0] if not value.empty else ""

        if pd.isna(value):
            return ""

        value = str(value).strip()
        return " ".join(value.split())



    