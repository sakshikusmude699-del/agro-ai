"""
Database connection manager using Motor (async MongoDB driver).
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# Global DB reference
client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """Connect to MongoDB Atlas."""
    global client, db
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/agrosmart")
    client = AsyncIOMotorClient(uri)
    db = client.agrosmart
    print("✅ Connected to MongoDB Atlas")


async def disconnect_db():
    """Disconnect from MongoDB."""
    global client
    if client:
        client.close()
        print("🔌 Disconnected from MongoDB")


def get_db():
    """Return the active database instance."""
    return db
