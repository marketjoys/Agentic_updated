#!/usr/bin/env python3
"""
Test script to debug and fix follow-up scheduling system
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

async def setup_test_follow_up_scenario():
    """Set up a realistic test scenario for follow-up scheduling"""
    
    print("🔄 Setting up test follow-up scenario...")
    
    # Connect to database
    await db_service.connect()
    
    # Get the campaign we created
    campaign_id = "3ee20ea2-0409-47c3-ad4b-d69d0278bf33"
    campaign = await db_service.get_campaign_by_id(campaign_id)
    
    if not campaign:
        print(f"❌ Campaign {campaign_id} not found")
        return False
    
    print(f"✅ Found campaign: {campaign['name']}")
    
    # Get prospects from the campaign
    prospects = []
    for list_id in campaign.get('list_ids', []):
        list_prospects = await db_service.get_prospects_by_list_id(list_id)
        prospects.extend(list_prospects)
    
    print(f"✅ Found {len(prospects)} prospects")
    
    # Create successful email records for each prospect
    email_provider_id = "f22429c6-74e6-4f35-9d0d-b70f82effe79"
    sent_time = datetime.utcnow() - timedelta(minutes=3)  # 3 minutes ago to trigger 2-minute follow-up
    
    for prospect in prospects:
        # Create a successful email record
        email_record = {
            "id": generate_id(),
            "prospect_id": prospect["id"],
            "campaign_id": campaign_id,
            "email_provider_id": email_provider_id,
            "recipient_email": prospect["email"],
            "subject": f"Welcome to {prospect['company']} - Let's Connect!",
            "content": f"Hi {prospect['first_name']},\n\nTest email content...",
            "status": "sent",  # Mark as sent successfully
            "sent_at": sent_time,
            "is_follow_up": False,
            "follow_up_sequence": 0,
            "created_at": sent_time,
            "sent_by_us": True,
            "thread_id": f"thread_{prospect['id']}",
            "template_id": campaign["template_id"],
            "provider_name": "Test Gmail Provider"
        }
        
        await db_service.create_email_record(email_record)
        
        # Update prospect to enable follow-ups
        await db_service.update_prospect(prospect["id"], {
            "last_contact": sent_time,
            "follow_up_status": "active",
            "follow_up_count": 0,
            "campaign_id": campaign_id,
            "email_provider_id": email_provider_id,
            "updated_at": datetime.utcnow()
        })
        
        # Create thread context for tracking
        await enhanced_db_service.create_or_update_thread_context(
            prospect["id"], 
            campaign_id, 
            email_provider_id,
            {
                "type": "sent",
                "recipient": prospect["email"],
                "subject": email_record["subject"],
                "content": email_record["content"],
                "timestamp": sent_time,
                "is_follow_up": False,
                "follow_up_sequence": 0,
                "email_id": email_record["id"],
                "template_id": campaign["template_id"],
                "provider_id": email_provider_id,
                "sent_by_us": True
            }
        )
        
        print(f"✅ Set up follow-up tracking for {prospect['email']}")
    
    # Update campaign status to active
    await db_service.update_campaign(campaign_id, {
        "status": "active",
        "updated_at": datetime.utcnow()
    })
    
    print("✅ Test scenario setup complete!")
    return True

async def check_follow_up_readiness():
    """Check if prospects are ready for follow-ups"""
    
    print("\n🔍 Checking follow-up readiness...")
    
    await db_service.connect()
    
    # Get active campaigns with follow-up enabled
    campaigns = await enhanced_db_service.get_active_follow_up_campaigns_enhanced()
    print(f"✅ Found {len(campaigns)} active follow-up campaigns")
    
    for campaign in campaigns:
        campaign_id = campaign["id"]
        print(f"\n📧 Campaign: {campaign['name']}")
        print(f"   - Follow-up intervals: {campaign.get('follow_up_intervals', [])}")
        print(f"   - Time window: {campaign.get('follow_up_time_window_start', '00:00')} - {campaign.get('follow_up_time_window_end', '23:59')}")
        
        # Get prospects needing follow-up
        prospects_needing_follow_up = await enhanced_db_service.get_prospects_needing_follow_up_enhanced(campaign_id)
        print(f"   - Prospects needing follow-up: {len(prospects_needing_follow_up)}")
        
        for prospect in prospects_needing_follow_up:
            print(f"     * {prospect['email']}")
            print(f"       - Last contact: {prospect.get('last_contact', 'Never')}")
            print(f"       - Follow-up count: {prospect.get('follow_up_count', 0)}")
            print(f"       - Follow-up status: {prospect.get('follow_up_status', 'unknown')}")
            
            # Check time since last contact
            if prospect.get('last_contact'):
                time_since_last = datetime.utcnow() - prospect['last_contact']
                minutes_since = time_since_last.total_seconds() / 60
                print(f"       - Minutes since last contact: {minutes_since:.1f}")
                
                # Check if ready for 2-minute follow-up
                if minutes_since >= 2:
                    print(f"       - ✅ Ready for follow-up (>= 2 minutes)")
                else:
                    print(f"       - ⏳ Not yet ready (needs {2 - minutes_since:.1f} more minutes)")

async def test_follow_up_engine_logic():
    """Test the follow-up engine logic directly"""
    
    print("\n🧪 Testing follow-up engine logic...")
    
    from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
    
    # Get engine status
    is_running = enhanced_smart_follow_up_engine.processing
    print(f"✅ Follow-up engine running: {is_running}")
    
    if not is_running:
        print("🚀 Starting follow-up engine...")
        result = await enhanced_smart_follow_up_engine.start_follow_up_engine()
        print(f"Engine start result: {result}")
    
    # Manually trigger follow-up check
    print("🔄 Manually triggering follow-up check...")
    await enhanced_smart_follow_up_engine._check_and_send_follow_ups()
    
    # Get statistics
    stats = await enhanced_smart_follow_up_engine.get_enhanced_follow_up_statistics()
    print(f"📊 Follow-up Statistics:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")

async def main():
    """Main test function"""
    print("🚀 Starting Follow-up Scheduling Debug Session\n")
    
    # Setup test scenario
    success = await setup_test_follow_up_scenario()
    if not success:
        print("❌ Failed to set up test scenario")
        return
    
    # Wait a moment
    print("\n⏳ Waiting 5 seconds for systems to process...")
    await asyncio.sleep(5)
    
    # Check follow-up readiness
    await check_follow_up_readiness()
    
    # Test engine logic
    await test_follow_up_engine_logic()
    
    # Final status check
    print("\n📊 Final System Status Check:")
    
    # Check campaign
    campaign = await db_service.get_campaign_by_id("3ee20ea2-0409-47c3-ad4b-d69d0278bf33")
    if campaign:
        print(f"✅ Campaign '{campaign['name']}' status: {campaign.get('status', 'unknown')}")
        
        # Check for any follow-up emails sent
        follow_up_emails = await db_service.db.emails.find({
            "campaign_id": campaign["id"],
            "is_follow_up": True
        }).to_list(length=100)
        
        print(f"📧 Follow-up emails sent: {len(follow_up_emails)}")
        for email in follow_up_emails:
            print(f"   - To: {email.get('recipient_email', 'Unknown')}")
            print(f"     Subject: {email.get('subject', 'No subject')}")
            print(f"     Status: {email.get('status', 'Unknown')}")
            print(f"     Sent at: {email.get('sent_at', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(main())