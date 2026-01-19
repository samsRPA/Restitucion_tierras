from pathlib import Path
import requests
import logging
from app.domain.interfaces.IGetDataService import IGetDataService
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class GetDataService(IGetDataService):
    
    logger= logging.getLogger(__name__)
    
    def __init__(self):
        pass
    
    def get_report_dates_states(self, codigo: str, annio_actual: str, despacho_judicial: str, ciudad:str):
        url = (
            "https://apiportalrestituciondetierras.ramajudicial.gov.co/"
            f"api/Reporte/Estado/FechasEstado/{codigo}/{annio_actual}"
        )

        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            response = session.get(url, timeout=60)

            # 🔹 LOG DEL STATUS CODE
            self.logger.info(
                f"🌐 [HTTP {response.status_code}] Consulta estados → {despacho_judicial} de la ciudad {ciudad}"
            )

            response.raise_for_status()
            payload = response.json()

            # 🔹 Validaciones estructurales
            if not isinstance(payload, dict):
                self.logger.warning("⚠️ Respuesta no es un JSON válido")
                return None

            if not payload.get("success", False):
                self.logger.warning(
                    f"⚠️ API respondió success=false → {payload}"
                )
                return None

            estados = payload.get("data")

            # 🔹 Validar data
            
         

            if not isinstance(estados, list):
                self.logger.warning(
                    f"⚠️ 'data' no es una lista → {type(estados)}"
                )
                return None

            return estados

        except requests.exceptions.Timeout:
            self.logger.error("⏳ Timeout consultando estados")
            return None

        except requests.exceptions.HTTPError as e:
            self.logger.error(
                f"⚠️ HTTP {e.response.status_code} → {e.response.text}"
            )
            return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Error Request → {str(e)}")
            return None

        except Exception as e:
            self.logger.exception("🔥 Error inesperado")
            return None


    def get_state(self, codigo: str, key: str, id: int, despacho_judicial: str, ciudad: str):
        url = (
            "https://apiportalrestituciondetierras.ramajudicial.gov.co/"
            f"api/Reporte/reporte-estado/{codigo}/{key}/{id}"
        )

        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            response = session.get(url, timeout=60)

            # 🔹 LOG DIFERENCIADO
            self.logger.info(
                f"📄 [HTTP {response.status_code}] "
                f"Detalle de estado obtenido | Fecha={key} | "
                f"Despacho={despacho_judicial} | Ciudad={ciudad}"
            )

            response.raise_for_status()
            payload = response.json()

            # 🔹 Validación de estructura
            if not isinstance(payload, dict):
                self.logger.warning("🧩 Respuesta inesperada → El payload no es un objeto JSON")
                return None

            if not payload.get("success", False):
                self.logger.warning(
                    f"🚫 Estado no disponible → API indicó success=false | Payload={payload}"
                )
                return None

            estado = payload.get("data")

            # 🔹 Validación de contenido
            if not isinstance(estado, dict):
                self.logger.warning(
                    f"📦 Formato inválido → 'data' no es un dict ({type(estado)})"
                )
                return None

            self.logger.info(
                f"✅ Estado procesado correctamente | "
                f"Despacho={despacho_judicial} | Fecha={key}"
            )

            return estado

        except requests.exceptions.Timeout:
            self.logger.error(
                f"⏱️ Tiempo de espera agotado consultando el estado | "
                f"Despacho={despacho_judicial} | Fecha={key}"
            )
            return None

        except requests.exceptions.HTTPError as e:
            self.logger.error(
                f"📛 Error HTTP al obtener estado | "
                f"Status={e.response.status_code} | "
                f"Respuesta={e.response.text}"
            )
            return None

        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"🔌 Falla de comunicación con la API de estados → {str(e)}"
            )
            return None

        except Exception:
            self.logger.exception(
                "🔥 Excepción crítica durante la consulta del detalle del estado"
            )
            return None



