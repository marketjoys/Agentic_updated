#!/usr/bin/env python3
"""
Follow-up Fix Test - Test if follow-ups work after setting default provider
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import sys
import os

# Backend URL from environment
BACKEND_URL = "https://9875c261-7164-46da-a66e-4f7aea2c987d.preview.emergentagent.com/api"

async def test_follow_up_fix():
    """Test if follow-up emails work after fixing the default provider issue"""
    
    session = aiohttp.ClientSession()
    
    try:
        print("🔍 TESTING FOLLOW-UP FIX")
        print("=" * 50)
        
        # Create a simple campaign with follow-up
        campaign_data = {
            "name": f"Follow-up Fix Test - {datetime.now().strftime('%H:%M:%S')}",
            "template_id": "be101ac3-a397-4ff2-8381-4d08f49fabce",  # Welcome Email template
            "list_ids": ["39e464c9-78d4-4653-adb5-71d26bf1ed09"],  # Previous test list
            "max_emails": 5,
            "schedule": None,
            "follow_up_enabled": True,
            "follow_up_schedule_type": "datetime",
            "follow_up_intervals": [1, 2],  # 1, 2 minutes for quick testing
            "follow_up_dates": [
                (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                (datetime.utcnow() + timedelta(minutes=2)).isoformat()
            ],
            "follow_up_timezone": "UTC",
            "follow_up_time_window_start": "00:00",
            "follow_up_time_window_end": "23:59",
            "follow_up_days_of_week": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
            "follow_up_templates": []
        }
        
        # Create campaign
        async with session.post(f"{BACKEND_URL}/campaigns", json=campaign_data) as response:
            if response.status == 200:
                campaign_result = await response.json()
                campaign_id = campaign_result["id"]
                print(f"✅ Campaign created: {campaign_id}")
                print(f"   Name: {campaign_result['name']}")
                print(f"   Follow-up enabled: {campaign_result['follow_up_enabled']}")
            else:
                print(f"❌ Failed to create campaign: {response.status}")
                return
        
        # Send campaign
        send_data = {
            "send_immediately": True,
            "email_provider_id": "",  # Use default
            "max_emails": 5,
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [1, 2],
            "follow_up_templates": []
        }
        
        async with session.post(f"{BACKEND_URL}/campaigns/{campaign_id}/send", json=send_data) as response:
            if response.status == 200:
                send_result = await response.json()
                print(f"✅ Campaign sent successfully")
                print(f"   Total sent: {send_result.get('total_sent', 0)}")
                print(f"   Total failed: {send_result.get('total_failed', 0)}")
            else:
                print(f"❌ Failed to send campaign: {response.status}")
                return
        
        # Monitor for follow-ups for 3 minutes
        print(f"\n👀 Monitoring for follow-ups (3 minutes)...")
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=3)
        
        previous_count = 0
        
        while datetime.utcnow() < end_time:
            current_time = datetime.utcnow()
            
            # Get campaign details
            async with session.get(f"{BACKEND_URL}/campaigns/{campaign_id}") as response:
                if response.status == 200:
                    campaign = await response.json()
                    email_records = campaign.get("email_records", [])
                    
                    # Filter for kasargovinda@gmail.com
                    kasargovinda_emails = [
                        record for record in email_records 
                        if record.get("recipient_email") == "kasargovinda@gmail.com"
                    ]
                    
                    if len(kasargovinda_emails) > previous_count:
                        new_emails = kasargovinda_emails[previous_count:]
                        print(f"\n📧 {current_time.strftime('%H:%M:%S')} - Found {len(new_emails)} new email(s)!")
                        
                        for email in new_emails:
                            print(f"   • Subject: {email.get('subject', 'N/A')}")
                            print(f"     Status: {email.get('status', 'N/A')}")
                            print(f"     Is Follow-up: {email.get('is_follow_up', False)}")
                            print(f"     Follow-up Sequence: {email.get('follow_up_sequence', 'N/A')}")
                            print(f"     Sent At: {email.get('sent_at', 'N/A')}")
                        
                        previous_count = len(kasargovinda_emails)
                    else:
                        print(f"⏰ {current_time.strftime('%H:%M:%S')} - No new emails (total: {len(kasargovinda_emails)})")
            
            await asyncio.sleep(20)  # Check every 20 seconds
        
        print(f"\n✅ Monitoring completed")
        
        # Final check
        async with session.get(f"{BACKEND_URL}/campaigns/{campaign_id}") as response:
            if response.status == 200:
                campaign = await response.json()
                email_records = campaign.get("email_records", [])
                
                kasargovinda_emails = [
                    record for record in email_records 
                    if record.get("recipient_email") == "kasargovinda@gmail.com"
                ]
                
                initial_emails = [e for e in kasargovinda_emails if not e.get('is_follow_up', False)]
                follow_up_emails = [e for e in kasargovinda_emails if e.get('is_follow_up', False)]
                
                print(f"\n📊 FINAL RESULTS:")
                print(f"   Total emails for kasargovinda@gmail.com: {len(kasargovinda_emails)}")
                print(f"   Initial emails: {len(initial_emails)}")
                print(f"   Follow-up emails: {len(follow_up_emails)}")
                
                if len(follow_up_emails) > 0:
                    print(f"   ✅ SUCCESS: Follow-up emails are now working!")
                    for i, email in enumerate(follow_up_emails, 1):
                        print(f"      {i}. Sequence {email.get('follow_up_sequence', 'N/A')} - {email.get('sent_at', 'N/A')}")
                else:
                    print(f"   ❌ No follow-up emails generated")
    
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_follow_up_fix())