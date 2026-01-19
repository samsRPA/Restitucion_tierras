from dependency_injector import containers, providers
from app.application.services.scrapper.ScrapperService import ScrapperService
from app.domain.interfaces.IRabbitMQConsumer import IRabbitMQConsumer
from app.domain.interfaces.IScrapperService import IScrapperService
from app.infrastucture.config.Settings import Settings
from app.infrastucture.rabbitmq.RabbitMQConsumer import RabbitMQConsumer
from app.domain.interfaces.IProcessDataService import IProcessDataService
from app.application.services.scrapper.ProcessDataService import ProcessDataService
from app.application.services.scrapper.GetDataService import GetDataService
from app.domain.interfaces.IGetDataService import IGetDataService
from app.domain.interfaces.IDataBase import IDataBase
from app.infrastucture.database.OracleDB import OracleDB
from app.application.services.scrapper.LandRestScrapperEdicts import LandRestScrapperEdicts
from app.domain.interfaces.ILandRestScrapperEdicts import ILandRestScrapperEdicts

from app.domain.interfaces.IS3Manager import IS3Manager
from app.infrastucture.AWS.S3Manager import S3Manager
from app.infrastucture.database.repositories.TControlRep import TControlRep
from app.infrastucture.database.repositories.TorreAwsRep import TorreAwsRep
from app.domain.interfaces.IUploadDataService import IUploadDataService
from app.application.services.scrapper.UploadDataService import UploadDataService
from app.application.services.scrapper.BrowserService import BrowserService
from app.domain.interfaces.IBrowserService import IBrowserService

class Dependencies(containers.DeclarativeContainer):
    config = providers.Configuration()
    settings: providers.Singleton[Settings] = providers.Singleton(Settings)

    data_base: providers.Singleton[IDataBase] = providers.Singleton(
        OracleDB,
        db_user=settings.provided.data_base.DB_USER,
        db_password=settings.provided.data_base.DB_PASSWORD,
        db_host=settings.provided.data_base.DB_HOST,
        db_port=settings.provided.data_base.DB_PORT,
        db_service_name=settings.provided.data_base.DB_SERVICE_NAME,
    )

    browser_service: providers.Factory[IBrowserService] = providers.Factory(
        BrowserService,
       
    )
    

    S3_manager : providers.Singleton[IS3Manager] = providers.Singleton(
        S3Manager,
        awsAccessKey = settings.provided.s3.awsAccessKey,
        awsSecretKey = settings.provided.s3.awsSecretKey,
        bucketName = settings.provided.s3.bucketLitigando,
        s3Prefix = settings.provided.s3.prefixLitigando,
    )

    torre_aws_rep = providers.Factory(
        TorreAwsRep,
        seqAws=settings.provided.data_base.SEQ_TORRE_ARCHIVOS_AWS,
        table=settings.provided.data_base.TB_TORRE_ARCHIVOS_AWS,
       
    )
 
    torre_control_rep = providers.Factory(
        TControlRep,
        table=settings.provided.data_base.TB_TORRE_CONTROL
       
    )

    get_data_service: providers.Factory[IGetDataService] = providers.Factory(
        GetDataService,
    )
    
    process_data_service: providers.Factory[IProcessDataService] = providers.Factory(
        ProcessDataService,
       
    )
    upload_data_service: providers.Factory[IUploadDataService] = providers.Factory(
        UploadDataService,
        torre_aws_rep,
        torre_control_rep,
        get_data_service,
        process_data_service,
        S3_manager
    )



    land_rest_scrapper_edicts: providers.Factory[ILandRestScrapperEdicts] = providers.Factory(
        LandRestScrapperEdicts,
        data_base,
        get_data_service,
        upload_data_service ,
        browser_service
    )

    scrapper_service: providers.Factory[IScrapperService] = providers.Factory(
        ScrapperService,
        land_rest_scrapper_edicts =land_rest_scrapper_edicts
    )




   
    # Provider del consumidor
    rabbitmq_consumer: providers.Singleton[IRabbitMQConsumer] = providers.Singleton(
        RabbitMQConsumer,
        host=settings.provided.rabbitmq.HOST,
        port=settings.provided.rabbitmq.PORT,
        pub_queue_name=settings.provided.rabbitmq.PUB_QUEUE_NAME,
        prefetch_count=settings.provided.rabbitmq.PREFETCH_COUNT,
        scrapper_service=scrapper_service.provider,
        user=settings.provided.rabbitmq.RABBITMQ_USER,
        password=settings.provided.rabbitmq.RABBITMQ_PASS
    )
