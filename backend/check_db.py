#!/usr/bin/env python3
"""
Quick script to check database contents
"""
import asyncio
import sys
sys.path.append('/app/backend')

from app.services.database import db_service

async def check_database():
    await db_service.connect()
    
    # Check templates
    templates = await db_service.get_templates()
    print(f"📝 Templates: {len(templates)}")
    for t in templates:
        print(f"  - {t['name']}")
    
    # Check prospects
    prospects = await db_service.get_prospects()
    print(f"👥 Prospects: {len(prospects)}")
    for p in prospects:
        print(f"  - {p['first_name']} {p['last_name']} ({p['email']})")
    
    # Check lists
    lists = await db_service.get_lists()
    print(f"📋 Lists: {len(lists)}")
    for l in lists:
        print(f"  - {l['name']} ({l['prospect_count']} prospects)")
    
    # Check campaigns
    campaigns = await db_service.get_campaigns()
    print(f"🚀 Campaigns: {len(campaigns)}")
    for c in campaigns:
        print(f"  - {c['name']} (status: {c['status']}, list_ids: {c.get('list_ids', [])})")
    
    # Check email providers
    providers = await db_service.get_email_providers()
    print(f"📧 Email Providers: {len(providers)}")
    for p in providers:
        print(f"  - {p['name']} ({p['email_address']})")
    
    await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(check_database())