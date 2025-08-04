#!/usr/bin/env python3
"""
Immediate test script for follow-up scheduling with real-time verification
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend app to the Python path
sys.path.append('/app/backend')

from app.services.database import db_service
from app.services.enhanced_database import enhanced_db_service
from app.utils.helpers import generate_id

async def force_follow_up_test():
    """Force a follow-up test with optimal conditions"""
    
    print("🚀 Starting Immediate Follow-up Test...")
    
    await db_service.connect()
    
    # Get prospects
    prospects = await db_service.get_prospects()
    campaign_id = "3ee20ea2-0409-47c3-ad4b-d69d0278bf33"
    
    if not prospects:
        print("❌ No prospects found")
        return
    
    print(f"✅ Found {len(prospects)} prospects")
    
    # Force immediate follow-up timing for testing
    email_provider_id = "f22429c6-74e6-4f35-9d0d-b70f82effe79"
    sent_time = datetime.utcnow() - timedelta(minutes=5)  # 5 minutes ago
    
    for prospect in prospects[:1]:  # Test with just one prospect
        # Update prospect to be ready for immediate follow-up
        await db_service.update_prospect(prospect["id"], {
            "last_contact": sent_time,
            "follow_up_status": "active",
            "follow_up_count": 0,
            "campaign_id": campaign_id,
            "email_provider_id": email_provider_id,
            "updated_at": datetime.utcnow()
        })
        
        print(f"✅ Updated prospect {prospect['email']} for immediate follow-up")
        
        # Check current time
        current_time = datetime.utcnow()
        print(f"🕐 Current time: {current_time}")
        print(f"📧 Last contact: {sent_time}")
        print(f"⏱️  Minutes since last contact: {(current_time - sent_time).total_seconds() / 60:.1f}")
    
    # Manually trigger follow-up engine
    from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
    
    print("\n🔄 Manually triggering follow-up check...")
    await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
    
    # Wait a moment and check results
    await asyncio.sleep(2)
    
    # Check for sent follow-ups
    follow_up_emails = await db_service.db.emails.find({
        "campaign_id": campaign_id,
        "is_follow_up": True
    }).to_list(length=100)
    
    print(f"\n📊 Results:")
    print(f"Follow-up emails sent: {len(follow_up_emails)}")
    
    if follow_up_emails:
        for email in follow_up_emails:
            print(f"✅ Follow-up sent to: {email.get('recipient_email')}")
            print(f"   Subject: {email.get('subject')}")
            print(f"   Status: {email.get('status')}")
            print(f"   Sequence: {email.get('follow_up_sequence')}")
            print(f"   Sent at: {email.get('sent_at')}")
    else:
        print("❌ No follow-up emails were sent")
        
        # Debug: Check what the engine is seeing
        print("\n🔍 Debug Information:")
        campaigns = await enhanced_db_service.get_active_follow_up_campaigns_enhanced()
        print(f"Active campaigns: {len(campaigns)}")
        
        if campaigns:
            campaign = campaigns[0]
            prospects_needing = await enhanced_db_service.get_prospects_needing_follow_up_enhanced(campaign["id"])
            print(f"Prospects needing follow-up: {len(prospects_needing)}")
            
            for prospect in prospects_needing[:1]:
                print(f"Prospect: {prospect['email']}")
                print(f"  - Last contact: {prospect.get('last_contact')}")
                print(f"  - Follow-up status: {prospect.get('follow_up_status')}")
                print(f"  - Follow-up count: {prospect.get('follow_up_count')}")
                
                # Check if in time window
                current_time = datetime.utcnow()
                current_day = current_time.strftime("%A").lower()
                current_time_str = current_time.strftime("%H:%M")
                
                print(f"  - Current day: {current_day}")
                print(f"  - Current time: {current_time_str}")
                print(f"  - Campaign time window: {campaign.get('follow_up_time_window_start', '00:00')} - {campaign.get('follow_up_time_window_end', '23:59')}")
                print(f"  - Campaign allowed days: {campaign.get('follow_up_days_of_week', [])}")
                
                # Check time window manually
                start_time = campaign.get("follow_up_time_window_start", "00:00")
                end_time = campaign.get("follow_up_time_window_end", "23:59")
                allowed_days = campaign.get("follow_up_days_of_week", [])
                
                in_time_window = start_time <= current_time_str <= end_time
                day_allowed = current_day in allowed_days
                
                print(f"  - In time window: {in_time_window}")
                print(f"  - Day allowed: {day_allowed}")
                print(f"  - Can send now: {in_time_window and day_allowed}")

if __name__ == "__main__":
    asyncio.run(force_follow_up_test())