
import logging
import csv
from pathlib import Path
from reportlab.platypus import (
SimpleDocTemplate, Paragraph, Spacer,
Table, TableStyle, KeepInFrame
)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from pathlib import Path
from datetime import datetime

from app.domain.interfaces.IProcessDataService import IProcessDataService
import re
class ProcessDataService(IProcessDataService,):
    
    logger= logging.getLogger(__name__)
    
    def __init__(self):
        pass
        


    def generate_fijaciones_csv( self, fijaciones: list,  output_path: str):
        """
        Genera un CSV con las fijaciones de estado.

        Columnas:
        filename | radicado | tipo | demandante | demandado | resuelve | fecha
        """

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        headers = [
            "filename",
            "radicado",
            "tipo",
            "demandante",
            "demandado",
            "resuelve",
            "fecha"
        ]

        try:
            with output_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for item in fijaciones:
                    radicado=self.normalize_text(item.get("codProceso", ""))
                    writer.writerow({
                    "filename": output_path.name,
                    "radicado": radicado,
                    "tipo": self.normalize_text(item.get("clase", "")),
                    "demandante": self.normalize_text(item.get("demandantes", "")),
                    "demandado": self.normalize_text(item.get("demandados",  radicado)),
                    "resuelve": self.normalize_text(item.get("descripcionActuacion", "")),
                    "fecha": self.normalize_text(item.get("fechaProvidencia", "")),
                })


            self.logger.info(
                f"📄 CSV de fijaciones generado correctamente → {output_path}"
            )

        except Exception as e:
            self.logger.error(
                f"❌ Error generando CSV de fijaciones: {e}",
                exc_info=True
            )




    def normalize_text(self, value: str) -> str:
        """
        Normaliza texto para PDF y CSV:
        &  -> Y
        '  -> espacio
        '' -> espacio
        *  -> espacio
        """
        if not value:
            return ""

        text = str(value)

        replacements = {
            "&": " Y ",
            "'": " ",
            "*": " ",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Eliminar comillas dobles si vienen repetidas
        text = text.replace("''", " ")

        # Normalizar espacios
        text = re.sub(r"\s+", " ", text)

        return text.strip()
