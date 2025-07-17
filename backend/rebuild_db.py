#!/usr/bin/env python3
"""
Script to clean database completely and recreate with clean data
"""
import asyncio
import sys
sys.path.append('/app/backend')

from app.services.database import db_service
from app.services.seed_data import initialize_seed_data

async def rebuild_database():
    await db_service.connect()
    
    # Drop all collections
    await db_service.db.drop_collection("templates")
    await db_service.db.drop_collection("prospects")
    await db_service.db.drop_collection("prospect_lists")
    await db_service.db.drop_collection("campaigns")
    await db_service.db.drop_collection("email_providers")
    await db_service.db.drop_collection("intents")
    await db_service.db.drop_collection("emails")
    await db_service.db.drop_collection("threads")
    
    print("🧹 Dropped all collections")
    
    # Recreate seed data
    await initialize_seed_data(db_service)
    
    await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(rebuild_database())