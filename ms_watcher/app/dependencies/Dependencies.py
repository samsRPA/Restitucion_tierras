

from dependency_injector import containers, providers

from app.infrastucture.config.Settings import Settings
from app.domain.interfaces.IRabbitMQProducer import IRabbitMQProducer
from app.infrastucture.rabbitmq.RabbitMQProducer import RabbitMQProducer


from app.domain.interfaces.IDataBase import IDataBase

from app.infrastucture.database.OracleDB import OracleDB


from app.application.service.GetOfficesService import GetOfficesService
from app.domain.interfaces.IGetOfficesService import IGetOfficesService
from app.domain.interfaces.IOfficesLandRestitution import IOfficesLandRestitution
from app.application.service.OfficesLandRestitution import OfficesLandRestitution
from app.infrastucture.database.repositories.KeysLandRestitutionRepository import KeysLandRestitutionRepository





class Dependencies(containers.DeclarativeContainer):
  config = providers.Configuration()
  settings: providers.Singleton[Settings] = providers.Singleton(Settings)
  wiring_config = containers.WiringConfiguration(
     modules=["app.api.routes.land_restitution_routes"]
  )

  data_base: providers.Singleton[IDataBase] = providers.Singleton(
        OracleDB,
        db_user=settings.provided.data_base.DB_USER,
        db_password=settings.provided.data_base.DB_PASSWORD,
        db_host=settings.provided.data_base.DB_HOST,
        db_port=settings.provided.data_base.DB_PORT,
        db_service_name=settings.provided.data_base.DB_SERVICE_NAME,
    )

  key_land_res_rep= providers.Factory(
   KeysLandRestitutionRepository,
       
  )

   
  get_data_service: providers.Factory[IGetOfficesService] = providers.Factory(
      GetOfficesService,
      db=data_base,
      repository=key_land_res_rep
      
    )



  rabbitmq_producer: providers.Singleton[IRabbitMQProducer] = providers.Singleton(
        RabbitMQProducer,
        host=settings.provided.rabbitmq.HOST,
        port=settings.provided.rabbitmq.PORT,
        pub_queue_states=settings.provided.rabbitmq.PUB_QUEUE_STATES,
        pub_queue_edicts=settings.provided.rabbitmq.PUB_QUEUE_EDICTS,
        user=settings.provided.rabbitmq.RABBITMQ_USER,
        password=settings.provided.rabbitmq.RABBITMQ_PASS
    )
 
  offices_land_restitution_service:  providers.Factory[IOfficesLandRestitution] = providers.Factory(
      OfficesLandRestitution,
      get_data_service,
      rabbitmq_producer
    )
