from fastapi import FastAPI, HTTPException, BackgroundTasks
from aiokafka import AIOKafkaConsumer
import asyncio
import os
# from google.protobuf.json_format import Parse
import logging

# Configuration settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "orders"

# Initialize FastAPI app
app = FastAPI()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Consumer
class KafkaConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
        )

    async def start(self):
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                order = order_pb2.Order()
                order.ParseFromString(msg.value)
                await self.process_order(order)
        finally:
            await self.consumer.stop()

    async def process_order(self, order):
        # Placeholder for notification processing logic
        logger.info(f"Processing order: {order.order_id}")
        for item in order.items:
            logger.info(f"Item: {item.product_id}, Quantity: {item.quantity}")
        # Here you would integrate with an email or SMS service to send notifications

# Protobuf message definitions
# from google.protobuf import message
# from google.protobuf.descriptor_pb2 import DescriptorProto

# class OrderItem(message.Message):
#     DESCRIPTOR = DescriptorProto(
#         name='OrderItem',
#         field=[
#             DescriptorProto.FieldDescriptorProto(name='product_id', number=1, type=9),
#             DescriptorProto.FieldDescriptorProto(name='quantity', number=2, type=5),
#         ],
#     )

# class Order(message.Message):
#     DESCRIPTOR = DescriptorProto(
#         name='Order',
#         field=[
#             DescriptorProto.FieldDescriptorProto(name='order_id', number=1, type=9),
#             DescriptorProto.FieldDescriptorProto(name='items', number=2, type=11, type_name='.OrderItem', label=3),
#         ],
#         nested_type=[
#             OrderItem.DESCRIPTOR,
#         ],
#     )

@app.on_event("startup")
async def startup_event():
    kafka_consumer = KafkaConsumer()
    asyncio.create_task(kafka_consumer.start())

@app.get("/health")
async def health_check():
    return {"status": "OK"}
