import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer
import asyncio
# import order_pb2

# Configuration settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "orders"

# Initialize FastAPI app
app = FastAPI()

# Kafka Producer
class KafkaProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_order(self, order):
        await self.producer.send_and_wait(KAFKA_TOPIC, order.SerializeToString())

kafka_producer = KafkaProducer()

@app.on_event("startup")
async def startup_event():
    await kafka_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()

# Pydantic models for request validation
class OrderItem(BaseModel):
    product_id: str
    quantity: int

class OrderRequest(BaseModel):
    order_id: str
    items: list[OrderItem]

@app.post("/orders")
async def create_order(order_request: OrderRequest):
    order = order_pb2.Order()
    order.order_id = order_request.order_id
    for item in order_request.items:
        order_item = order.items.add()
        order_item.product_id = item.product_id
        order_item.quantity = item.quantity
    
    try:
        await kafka_producer.send_order(order)
        return {"message": "Order created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

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
