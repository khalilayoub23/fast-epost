from typing import Any, Callable, Dict, List, Optional
import asyncio
import json
from datetime import datetime
from enum import Enum
import aio_pika

class QueuePriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class MessageQueue:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection = None
        self.channel = None
        self.queues: Dict[str, aio_pika.Queue] = {}
        self.consumers: Dict[str, List[Callable]] = {}

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.connection_url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def declare_queue(self, name: str, durable: bool = True):
        queue = await self.channel.declare_queue(
            name,
            durable=durable,
            arguments={
                'x-max-priority': 3
            }
        )
        self.queues[name] = queue
        return queue

    async def publish(
        self,
        queue_name: str,
        message: Any,
        priority: QueuePriority = QueuePriority.MEDIUM
    ):
        if queue_name not in self.queues:
            await self.declare_queue(queue_name)

        message_body = json.dumps({
            'data': message,
            'timestamp': datetime.utcnow().isoformat()
        }).encode()

        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                priority=priority.value,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )

    async def subscribe(self, queue_name: str, callback: Callable):
        if queue_name not in self.consumers:
            self.consumers[queue_name] = []
        self.consumers[queue_name].append(callback)

        if queue_name not in self.queues:
            await self.declare_queue(queue_name)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    for consumer in self.consumers[queue_name]:
                        await consumer(body['data'])
                except Exception as e:
                    print(f"Error processing message: {e}")

        await self.queues[queue_name].consume(process_message)