#!/usr/bin/env python3
"""
Script to clean up duplicate data in the database
"""
import asyncio
import sys
sys.path.append('/app/backend')

from app.services.database import db_service

async def clean_duplicates():
    await db_service.connect()
    
    # Delete all data to start fresh
    await db_service.db.templates.delete_many({})
    await db_service.db.prospects.delete_many({})
    await db_service.db.prospect_lists.delete_many({})
    await db_service.db.campaigns.delete_many({})
    await db_service.db.email_providers.delete_many({})
    await db_service.db.intents.delete_many({})
    
    print("🧹 Cleaned up all data from database")
    await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(clean_duplicates())