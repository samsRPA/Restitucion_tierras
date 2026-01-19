from abc import ABC, abstractmethod

class IRabbitMQProducer(ABC):

    @abstractmethod
    async def connect(self) -> None:
        pass


  
    @abstractmethod
    async def publishMessage(self, message):
        pass
        

    
    
    @abstractmethod
    async def close(self) -> None:
        pass


