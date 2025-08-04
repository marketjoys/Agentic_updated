#!/usr/bin/env python3
"""
Debug minute-based interval follow-up system
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

async def test_minute_based_intervals():
    """Test minute-based follow-up intervals"""
    
    print("🚀 Testing Minute-based Follow-up Intervals")
    
    await db_service.connect()
    
    # Update campaign to use minute-based intervals
    campaign_id = "3ee20ea2-0409-47c3-ad4b-d69d0278bf33"
    
    # First, let's see what's in the campaign currently
    campaign = await db_service.get_campaign_by_id(campaign_id)
    print(f"📧 Current campaign intervals: {campaign.get('follow_up_intervals', [])}")
    
    # Update campaign with shorter minute intervals for testing
    await db_service.update_campaign(campaign_id, {
        "follow_up_intervals": [1, 2, 3],  # 1, 2, 3 minutes
        "updated_at": datetime.utcnow()
    })
    print("✅ Updated campaign with 1, 2, 3 minute intervals")
    
    # Get a prospect and set last contact to be > 1 minute ago
    prospects = await db_service.get_prospects()
    if not prospects:
        print("❌ No prospects found")
        return
        
    prospect = prospects[0]
    print(f"🎯 Testing with prospect: {prospect['email']}")
    
    # Set last_contact to 2 minutes ago (should trigger 1-minute follow-up)
    email_provider_id = "f22429c6-74e6-4f35-9d0d-b70f82effe79"
    sent_time = datetime.utcnow() - timedelta(minutes=2)
    
    await db_service.update_prospect(prospect["id"], {
        "last_contact": sent_time,
        "follow_up_status": "active",
        "follow_up_count": 0,
        "campaign_id": campaign_id,
        "email_provider_id": email_provider_id,
        "updated_at": datetime.utcnow()
    })
    
    print(f"✅ Set last_contact to 2 minutes ago: {sent_time}")
    print(f"🕐 Current time: {datetime.utcnow()}")
    
    # Now manually trigger the follow-up engine
    from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
    
    print("\n🔄 Manually triggering follow-up check...")
    
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
    
    # Check results
    await asyncio.sleep(2)
    
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
            print(f"   Sequence: {email.get('follow_up_sequence')}")
            print(f"   Sent at: {email.get('sent_at')}")
    else:
        print("❌ No follow-up emails sent")
        
        # More detailed debugging
        print("\n🔍 Detailed Debug:")
        
        # Check prospect state
        updated_prospect = await db_service.get_prospect_by_id(prospect["id"])
        print(f"Prospect last_contact: {updated_prospect.get('last_contact')}")
        print(f"Prospect follow_up_count: {updated_prospect.get('follow_up_count', 0)}")
        print(f"Prospect follow_up_status: {updated_prospect.get('follow_up_status')}")
        
        # Calculate time difference manually
        current_time = datetime.utcnow()
        if updated_prospect.get('last_contact'):
            time_diff = current_time - updated_prospect['last_contact']
            minutes_diff = time_diff.total_seconds() / 60
            print(f"Minutes since last contact: {minutes_diff:.2f}")
            print(f"Should be >= 1 minute for first follow-up")
            
        # Check email provider
        provider = await db_service.get_email_provider_by_id(email_provider_id)
        if provider:
            print(f"Email provider found: {provider['name']}")
        else:
            print("❌ Email provider not found")
            
        # Check template
        campaign_updated = await db_service.get_campaign_by_id(campaign_id)
        template = await db_service.get_template_by_id(campaign_updated.get("template_id"))
        if template:
            print(f"Template found: {template['name']}")
        else:
            print("❌ Template not found")

if __name__ == "__main__":
    asyncio.run(test_minute_based_intervals())