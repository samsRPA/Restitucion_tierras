
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
        
    def generate_state_posting_pdf(self, notificacion: dict, output_path: str):
        """
        Genera el PDF de Fijación de Estado en A4 horizontal,
        tabla centrada, sin cortes y SIN LayoutError.
        """

        #base_dir = Path(__file__).resolve().parents[5]
        font_path = Path("/app/output/fonts/times.ttf")
        # ================== FUENTE ==================
        pdfmetrics.registerFont(
            TTFont("TimesNewRoman",  font_path)
        )

        fijaciones = notificacion.get("fijacionEstado", [])
        despacho_judicial = notificacion.get("despachoJudicial", "")
        firmante = notificacion.get("firmante", "")
        fecha_estado = notificacion.get("fechaEstado", "")
        consecutivo = notificacion.get("consecutivo", "")

        total_registros = len(fijaciones)
        fecha_estado_fmt = datetime.strptime(
            fecha_estado, "%Y-%m-%d"
        ).strftime("%d/%m/%Y")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ================== DOCUMENTO ==================
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            leftMargin=2.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(
            name="Titulo",
            fontName="Times-Bold",
            fontSize=12,
            alignment=1,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name="Subtitulo",
            fontName="Times-Bold",
            fontSize=11,
            alignment=1,
            spaceAfter=6
        ))

        styles.add(ParagraphStyle(
            name="NormalCentrado",
            fontName="Times-Bold",
            fontSize=9,
            alignment=1
        ))

        styles.add(ParagraphStyle(
            name="HeaderCell",
            fontName="Times-Bold",
            fontSize=8,
            alignment=1,
            leading=9
        ))

        styles.add(ParagraphStyle(
            name="Cell",
            fontName="TimesNewRoman",
            fontSize=7.5,
            leading=9,
            alignment=0
        ))

        styles.add(ParagraphStyle(
            name="TextoLegalCentrado",
            fontName="TimesNewRoman",
            fontSize=9,
            leading=11,
            alignment=1,
            spaceBefore=12
        ))

        # ================== HELPER CRÍTICO ==================
        def cell(text, style, max_height):
            """
            Limita la altura de cada celda para evitar LayoutError.
            """
            return KeepInFrame(
                0,
                max_height,
                [Paragraph(text or "", style)],
                mode="shrink"
            )

        elements = []

        # ================== ENCABEZADO ==================
        elements.append(Paragraph(
            "RAMA JUDICIAL<br/>"
            "CONSEJO SUPERIOR DE LA JUDICATURA<br/>"
            "REPÚBLICA DE COLOMBIA",
            styles["NormalCentrado"]
        ))

        elements.append(Spacer(1, 6))

        elements.append(
            Paragraph(despacho_judicial.upper(), styles["Titulo"])
        )
        elements.append(
            Paragraph(f"FIJACIÓN DE ESTADO # {consecutivo}", styles["Subtitulo"])
        )

        elements.append(Paragraph(
            f"<b>FECHA:</b> {fecha_estado_fmt} &nbsp;&nbsp;&nbsp; "
            f"<b>TOTAL REGISTROS:</b> {total_registros}",
            styles["NormalCentrado"]
        ))

        elements.append(Spacer(1, 10))

        # ================== TABLA ==================
        headers = [
            "NÚMERO DEL<br/>PROCESO",
            "CLASE DE<br/>PROCESO",
            "DEMANDANTES",
            "DEMANDADOS",
            "FECHA<br/>PROVIDENCIA",
            "DESCRIPCIÓN<br/>ACTUACIÓN",
            "ANOTACIÓN<br/>PROVIDENCIA",
            "DESPACHO",
            "DOCUMENTO"
        ]

        table_data = [
            [Paragraph(h, styles["HeaderCell"]) for h in headers]
        ]

        for item in fijaciones:
            table_data.append([
                cell(self.normalize_text(item.get("codProceso", "")), styles["Cell"], 2.5 * cm),
                cell(self.normalize_text(item.get("clase", "")), styles["Cell"], 2.5 * cm),
                cell(self.normalize_text(item.get("demandantes", "")), styles["Cell"], 4 * cm),
                cell(self.normalize_text(item.get("demandados", "")), styles["Cell"], 4 * cm),
                cell(self.normalize_text(item.get("fechaProvidencia", "")), styles["Cell"], 2 * cm),
                cell(self.normalize_text(item.get("descripcionActuacion", "")), styles["Cell"], 3 * cm),
                cell(self.normalize_text(item.get("anotacionActuacion", "")), styles["Cell"], 3 * cm),
                cell(self.normalize_text(item.get("despacho", "")), styles["Cell"], 4 * cm),
                cell("", styles["Cell"], 2 * cm),
            ])
        colWidths = [
            3.7 * cm,  # Número proceso
            2.2 * cm,  # Clase
            2.7 * cm,  # Demandantes
            3.7 * cm,  # Demandados
            2.5 * cm,  # Fecha
            2.5 * cm,  # Descripción
            2.5 * cm,  # Anotación
            2.7 * cm,  # Despacho
            2.2 * cm,  # Documento
        ]

        table = Table(
            table_data,
            colWidths=colWidths,
            repeatRows=1,
            splitByRow=1,
            hAlign="CENTER"
        )

        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        # ================== TEXTO LEGAL ==================
        elements.append(Paragraph(
            "Se fija el presente Estado por el término legal, al iniciar la jornada "
            "legal establecida para el Despacho judicial, y se desfija en la misma "
            "al terminar la jornada laboral del Despacho.",
            styles["TextoLegalCentrado"]
        ))

        elements.append(Spacer(1, 16))

        # ================== FIRMA ==================
        elements.append(Paragraph(
            f"{firmante}<br/>SECRETARIO",
            styles["NormalCentrado"]
        ))

        # ================== BUILD ==================
        doc.build(elements)
        # # ================== HASH SHA-256 ==================
        # sha256 = hashlib.sha256()
        # with open(output_path, "rb") as f:
        #     for block in iter(lambda: f.read(8192), b""):
        #         sha256.update(block)

        # pdf_hash = sha256.hexdigest()

        # self.logger.info(f"🔐 Hash PDF generado: {pdf_hash}")

        # return pdf_hash


    def generate_fijaciones_csv( self, fijaciones: list,  output_path: str):
        """
        Genera un CSV con las fijaciones de estado.

        Columnas:
        filename | radicado | tipo | demandante | demandado | resuelve | fecha
        """

        
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
