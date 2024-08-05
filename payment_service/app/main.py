import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer
import asyncio
# import payment_pb2

# Configuration settings
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "payments"

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

    async def send_payment(self, payment):
        await self.producer.send_and_wait(KAFKA_TOPIC, payment.SerializeToString())

kafka_producer = KafkaProducer()

@app.on_event("startup")
async def startup_event():
    await kafka_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()

# Pydantic models for request validation
class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    payment_method: str

@app.post("/payments")
async def process_payment(payment_request: PaymentRequest):
    payment = payment_pb2.Payment()
    payment.order_id = payment_request.order_id
    payment.amount = payment_request.amount
    payment.payment_method = payment_request.payment_method
    
    try:
        await kafka_producer.send_payment(payment)
        return {"message": "Payment processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "OK"}

# # Protobuf message definitions
# from google.protobuf import message
# from google.protobuf.descriptor_pb2 import DescriptorProto

# class Payment(message.Message):
#     DESCRIPTOR = DescriptorProto(
#         name='Payment',
#         field=[
#             DescriptorProto.FieldDescriptorProto(name='order_id', number=1, type=9),
#             DescriptorProto.FieldDescriptorProto(name='amount', number=2, type=2),
#             DescriptorProto.FieldDescriptorProto(name='payment_method', number=3, type=9),
#         ],
#     )