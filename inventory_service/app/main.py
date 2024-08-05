from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
import asyncio
import os
# from google.protobuf.json_format import Parse, MessageToJson

# Configuration settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/imtiaz_mart")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "orders"

# Database setup
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Models
class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    quantity = Column(Integer)

# Pydantic Schemas
class InventoryCreate(BaseModel):
    product_id: str
    quantity: int

class InventoryUpdate(BaseModel):
    product_id: str
    quantity: int

class InventoryResponse(BaseModel):
    product_id: str
    quantity: int

# CRUD operations
async def create_inventory(db: AsyncSession, inventory: InventoryCreate):
    db_inventory = Inventory(product_id=inventory.product_id, quantity=inventory.quantity)
    db.add(db_inventory)
    await db.commit()
    await db.refresh(db_inventory)
    return db_inventory

async def update_inventory(db: AsyncSession, inventory: InventoryUpdate):
    result = await db.execute(select(Inventory).filter(Inventory.product_id == inventory.product_id))
    db_inventory = result.scalar_one()
    db_inventory.quantity = inventory.quantity
    await db.commit()
    await db.refresh(db_inventory)
    return db_inventory

async def get_inventory(db: AsyncSession, product_id: str):
    result = await db.execute(select(Inventory).filter(Inventory.product_id == product_id))
    return result.scalar_one_or_none()

# Kafka Consumer
class KafkaConsumer:
    def __init__(self, db: AsyncSession):
        self.consumer = AIOKafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
        )
        self.db = db

    async def start(self):
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                order = order_pb2.Order()
                order.ParseFromString(msg.value)
                for item in order.items:
                    inventory = await get_inventory(self.db, item.product_id)
                    if inventory:
                        new_quantity = inventory.quantity - item.quantity
                        await update_inventory(self.db, InventoryUpdate(product_id=item.product_id, quantity=new_quantity))
        finally:
            await self.consumer.stop()

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = get_db()
    kafka_consumer = KafkaConsumer(db)
    asyncio.create_task(kafka_consumer.start())

@app.post("/inventory/", response_model=InventoryResponse)
async def create_inventory_item(inventory: InventoryCreate, db: AsyncSession = Depends(get_db)):
    db_inventory = await create_inventory(db, inventory)
    return db_inventory

@app.put("/inventory/{product_id}", response_model=InventoryResponse)
async def update_inventory_item(product_id: str, inventory: InventoryUpdate, db: AsyncSession = Depends(get_db)):
    db_inventory = await update_inventory(db, inventory)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory

@app.get("/inventory/{product_id}", response_model=InventoryResponse)
async def read_inventory_item(product_id: str, db: AsyncSession = Depends(get_db)):
    db_inventory = await get_inventory(db, product_id)
    if db_inventory is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_inventory

# # Protobuf message definitions
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
