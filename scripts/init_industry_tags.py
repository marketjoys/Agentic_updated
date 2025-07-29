#!/usr/bin/env python3
"""
Initialize default industry tags for AI prospecting
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.database import db_service
from app.utils.helpers import generate_id
from datetime import datetime

async def initialize_industry_tags():
    """Initialize default industry tags"""
    try:
        await db_service.connect()
        
        # Default industry tags based on Apollo.io common industries
        default_tags = [
            {"industry": "Accounting", "tag_id": "5567ce1f7369643b78570000", "description": "Accounting and financial services"},
            {"industry": "Agriculture", "tag_id": "55718f947369642142b84a12", "description": "Agriculture and farming"},
            {"industry": "Airlines/Aviation", "tag_id": "5567e0bf7369641d115f0200", "description": "Airlines and aviation industry"},
            {"industry": "Automotive", "tag_id": "5567ce1f7369643b78570001", "description": "Automotive and transportation"},
            {"industry": "Banking", "tag_id": "55718f947369642142b84a13", "description": "Banking and financial institutions"},
            {"industry": "Biotechnology", "tag_id": "5567e0bf7369641d115f0201", "description": "Biotechnology and life sciences"},
            {"industry": "Construction", "tag_id": "5567ce1f7369643b78570002", "description": "Construction and engineering"},
            {"industry": "Consulting", "tag_id": "55718f947369642142b84a14", "description": "Consulting services"},
            {"industry": "Consumer Goods", "tag_id": "5567e0bf7369641d115f0202", "description": "Consumer products and goods"},
            {"industry": "Education", "tag_id": "5567ce1f7369643b78570003", "description": "Education and training"},
            {"industry": "Energy", "tag_id": "55718f947369642142b84a15", "description": "Energy and utilities"},
            {"industry": "Entertainment", "tag_id": "5567e0bf7369641d115f0203", "description": "Entertainment and media"},
            {"industry": "Finance", "tag_id": "5567ce1f7369643b78570004", "description": "Financial services"},
            {"industry": "Food & Beverages", "tag_id": "55718f947369642142b84a16", "description": "Food and beverage industry"},
            {"industry": "Government", "tag_id": "5567e0bf7369641d115f0204", "description": "Government and public sector"},
            {"industry": "Healthcare", "tag_id": "5567ce1f7369643b78570005", "description": "Healthcare and medical services"},
            {"industry": "Hospitality", "tag_id": "55718f947369642142b84a17", "description": "Hotels and hospitality"},
            {"industry": "Information Technology", "tag_id": "5567e0bf7369641d115f0205", "description": "Information technology and services"},
            {"industry": "Insurance", "tag_id": "5567ce1f7369643b78570006", "description": "Insurance services"},
            {"industry": "Legal", "tag_id": "55718f947369642142b84a18", "description": "Legal services"},
            {"industry": "Manufacturing", "tag_id": "5567e0bf7369641d115f0206", "description": "Manufacturing and industrial"},
            {"industry": "Marketing", "tag_id": "5567ce1f7369643b78570007", "description": "Marketing and advertising"},
            {"industry": "Media", "tag_id": "55718f947369642142b84a19", "description": "Media and communications"},
            {"industry": "Non-Profit", "tag_id": "5567e0bf7369641d115f0207", "description": "Non-profit organizations"},
            {"industry": "Pharmaceuticals", "tag_id": "5567ce1f7369643b78570008", "description": "Pharmaceutical and drug companies"},
            {"industry": "Real Estate", "tag_id": "55718f947369642142b84a20", "description": "Real estate and property"},
            {"industry": "Retail", "tag_id": "5567e0bf7369641d115f0208", "description": "Retail and e-commerce"},
            {"industry": "Software", "tag_id": "5567ce1f7369643b78570009", "description": "Software development and tech"},
            {"industry": "Telecommunications", "tag_id": "55718f947369642142b84a21", "description": "Telecommunications and networking"},
            {"industry": "Transportation", "tag_id": "5567e0bf7369641d115f0209", "description": "Transportation and logistics"},
            {"industry": "Technology", "tag_id": "5567ce1f7369643b78570010", "description": "Technology companies"},
            {"industry": "Startups", "tag_id": "55718f947369642142b84a22", "description": "Startup companies"},
            {"industry": "SaaS", "tag_id": "5567e0bf7369641d115f0210", "description": "Software as a Service"},
            {"industry": "E-commerce", "tag_id": "5567ce1f7369643b78570011", "description": "E-commerce and online retail"},
            {"industry": "Fintech", "tag_id": "55718f947369642142b84a23", "description": "Financial technology"}
        ]
        
        # Check existing tags
        existing_tags = await db_service.get_industry_tags()
        existing_industries = {tag['industry'].lower() for tag in existing_tags}
        
        print(f"Found {len(existing_tags)} existing industry tags")
        
        # Filter out existing tags
        new_tags = []
        for tag in default_tags:
            if tag['industry'].lower() not in existing_industries:
                tag_data = {
                    "id": generate_id(),
                    "industry": tag['industry'],
                    "tag_id": tag['tag_id'],
                    "description": tag['description'],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                new_tags.append(tag_data)
        
        print(f"Adding {len(new_tags)} new industry tags")
        
        if new_tags:
            await db_service.bulk_insert_industry_tags(new_tags)
            print("✅ Successfully added industry tags:")
            for tag in new_tags:
                print(f"  • {tag['industry']} -> {tag['tag_id']}")
        else:
            print("✅ All industry tags already exist")
        
        # Display final count
        all_tags = await db_service.get_industry_tags()
        print(f"\n📊 Total industry tags in database: {len(all_tags)}")
        
    except Exception as e:
        print(f"❌ Error initializing industry tags: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await db_service.disconnect()

if __name__ == "__main__":
    print("🚀 Initializing AI Prospecting Industry Tags...")
    asyncio.run(initialize_industry_tags())
    print("✅ Industry tags initialization complete!")