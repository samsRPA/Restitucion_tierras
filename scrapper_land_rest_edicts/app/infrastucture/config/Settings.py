from pydantic_settings import BaseSettings


from app.infrastucture.config.RabbitMQSettings import RabbitMQSettings
from app.infrastucture.config.DataBaseSettings import DataBaseSettings
from app.infrastucture.config.S3ManagerSettings import S3ManagerSettings


class Settings(BaseSettings):
    rabbitmq : RabbitMQSettings = RabbitMQSettings()
    data_base: DataBaseSettings = DataBaseSettings()
    s3 : S3ManagerSettings = S3ManagerSettings()

def load_config() -> Settings:
    return Settings()
