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
                # row = (PROCESO_ID, INSTANCIA_RADICACION, ..., DEMANDADO

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

            return offices_list
        
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



    