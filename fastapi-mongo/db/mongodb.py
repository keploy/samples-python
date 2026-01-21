# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from quizzly.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client.quiz_app