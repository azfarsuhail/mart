import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from aiokafka import AIOKafkaProducer
import asyncio
# import user_pb2

# Configuration settings
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres:5432/imtiaz_mart")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = "users"

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

# Create tables
Base.metadata.create_all(bind=engine)

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

    async def send_user(self, user):
        await self.producer.send_and_wait(KAFKA_TOPIC, user.SerializeToString())

kafka_producer = KafkaProducer()

# FastAPI app initialization
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await kafka_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request validation
class UserCreate(BaseModel):
    username: str
    email: str

@app.post("/users", response_model=UserCreate)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create protobuf message
    # user_proto = user_pb2.User()
    # user_proto.id = db_user.id
    # user_proto.username = db_user.username
    # user_proto.email = db_user.email

    try:
        await kafka_producer.send_user(db_user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=UserCreate)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/health")
async def health_check():
    return {"status": "OK"}

# # Protobuf message definitions
# from google.protobuf import message
# from google.protobuf.descriptor_pb2 import DescriptorProto

# class User(message.Message):
#     DESCRIPTOR = DescriptorProto(
#         name='User',
#         field=[
#             DescriptorProto.FieldDescriptorProto(name='id', number=1, type=5),
#             DescriptorProto.FieldDescriptorProto(name='username', number=2, type=9),
#             DescriptorProto.FieldDescriptorProto(name='email', number=3, type=9),
#         ],
#     )
