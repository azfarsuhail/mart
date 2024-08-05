import asyncio
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
# from google.protobuf.json_format import MessageToDict
from typing import Dict

# Protobuf generated class
# from protobufs.product_pb2 import Product as ProductProto

# Initialize FastAPI app
app = FastAPI()

# In-memory database simulation
fake_products_db: Dict[int, Dict] = {}

# Pydantic model for Product
class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int

# Function to consume messages from Kafka
async def consume():
    consumer = AIOKafkaConsumer(
        'product-topic',
        bootstrap_servers='broker:9092',
        group_id="product-service-group"
    )
    await consumer.start()
    try:
        async for msg in consumer:
            logging.info("consumed: %s", msg.value)
            product_proto = ProductProto()
            product_proto.ParseFromString(msg.value)
            product_dict = MessageToDict(product_proto)
            fake_products_db[product_dict['id']] = product_dict
    finally:
        await consumer.stop()

# FastAPI endpoints
@app.post("/products", response_model=Product)
async def create_product(product: Product):
    if product.id in fake_products_db:
        raise HTTPException(status_code=400, detail="Product ID already exists")
    fake_products_db[product.id] = product.dict()
    return product

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = fake_products_db.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Startup event to initialize Kafka consumer
@app.on_event("startup")
async def startup_event():
    logging.info("Starting Kafka consumer")
    loop = asyncio.get_event_loop()
    loop.create_task(consume())