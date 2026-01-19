import json
import logging
import aio_pika

from app.domain.interfaces.IRabbitMQProducer import IRabbitMQProducer


class RabbitMQProducer(IRabbitMQProducer):

    def __init__(self, host, port, pub_queue_states ,pub_queue_edicts, user, password):
        self.host = host
        self.port = port
        self.pub_queue_states = pub_queue_states
        self.pub_queue_edicts= pub_queue_edicts
        self.user= user
        self.password = password
        self.connection = None
        self.channel = None
        self.logger= logging.getLogger(__name__)

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
            await self.channel.declare_queue(self.pub_queue_states, durable=True)
            await self.channel.declare_queue(self.pub_queue_edicts, durable=True)
         
            self.logger.info("✅ Conectado a RabbitMQ - Producer")

        except Exception as error:
            self.logger.error(f"❌ Error conectando al Producer: {error}")
            raise error

    async def publishMessage(self, message: dict):
        queues = [
            self.pub_queue_states,
            self.pub_queue_edicts,
        ]

        body = json.dumps(message).encode()

        for routing_key in queues:
            try:
                await self.channel.default_exchange.publish(
                    aio_pika.Message(
                        body=body,
                        delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT
                    ),
                    routing_key=routing_key,
                )

                self.logger.info(f"📤 Mensaje enviado a {routing_key}")

            except Exception as error:
                self.logger.exception(f"❌ Error enviando mensaje a {routing_key}")
                raise error

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            self.logger.info("🔌 Conexión con RabbitMQ cerrada")
