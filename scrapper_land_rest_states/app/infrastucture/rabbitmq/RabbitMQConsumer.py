import asyncio
import aio_pika
import logging
from typing import Callable

import time

from app.application.dto.ScrapperRequest import ScrapperRequest
from app.domain.interfaces.IRabbitMQConsumer import IRabbitMQConsumer
from app.domain.interfaces.IScrapperService import IScrapperService


class RabbitMQConsumer(IRabbitMQConsumer):

    def __init__(self, host: str, port: int, pub_queue_name: str, prefetch_count: int,
                 scrapper_service: Callable[[str], IScrapperService],user, password):
        self.host = host
        self.host = host
        self.port = port
        self.pub_queue_name = pub_queue_name
        self.prefetch_count = prefetch_count
        self.scrapper_service = scrapper_service
        self.queue: aio_pika.Queue | None = None
        self.channel: aio_pika.Channel | None = None
        self.connection: aio_pika.RobustConnection | None = None
        self.user = user
        self.password = password

        self.logger = logging.getLogger(__name__)
        
    async def connect(self) -> None:
        try:
            self.connection = await aio_pika.connect_robust(
                host=self.host,
                port=self.port,
                timeout=15,
                login=self.user,
                password=self.password,
           
            )
            self.channel = await self.connection.channel()

            await self.channel.set_qos(prefetch_count=self.prefetch_count)
            self.queue = await self.channel.declare_queue(
                self.pub_queue_name, durable=True
            )
            self.logger.info("✅ Conectado a RabbitMQ - Consumer")


        except Exception as error:
            self.logger.error(f"❌ Error conectando al consumer: {error}")
            raise error

    async def callback(self, message: aio_pika.IncomingMessage):
        self.logger.info("📥 Mensaje recibido")

        async with message.process():
            try:
                raw_body = message.body.decode()
             

                request = ScrapperRequest.fromRaw(raw_body)
                service = self.scrapper_service(request)

                self.logger.info("🚀 Ejecutando scrapper...")
                await service.runScrapper()
                self.logger.info("✅ Scrapper finalizado")

            except Exception as e:
                self.logger.exception("❌ Error procesando mensaje")
                raise


    async def startConsuming(self):
        if not self.channel or not self.queue:
            self.logger.info("📡 Conexión no establecida. Conectando...")
            await self.connect()

        await self.queue.consume(self.callback)
        self.logger.info("🎧 Esperando mensajes...")

        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("👋 Interrupción manual detectada.")
        finally:
            if self.connection:
                await self.connection.close()
                self.logger.info("🔌 Conexión a RabbitMQ cerrada.")
