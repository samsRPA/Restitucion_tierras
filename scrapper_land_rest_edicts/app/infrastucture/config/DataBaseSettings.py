from pydantic import Field
from app.infrastucture.config.EnvConfig import EnvConfig


class DataBaseSettings(EnvConfig):
    DB_USER: str = Field(..., alias='DB_USER')
    DB_PASSWORD: str = Field(..., alias='DB_PASSWORD')
    DB_HOST: str = Field(..., alias='DB_HOST')
    DB_PORT: int = Field(..., alias='DB_PORT')
    DB_SERVICE_NAME: str = Field(..., alias='DB_SERVICE_NAME')

    # 🔹 Tablas y secuencia
    TB_TORRE_CONTROL: str = Field(..., alias='TB_TORRE_CONTROL')
    TB_TORRE_ARCHIVOS_AWS: str = Field(..., alias='TB_TORRE_ARCHIVOS_AWS')
    SEQ_TORRE_ARCHIVOS_AWS: str = Field(..., alias='SEQ_TORRE_ARCHIVOS_AWS')
