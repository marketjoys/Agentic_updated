#!/usr/bin/env python3
"""
Deep debugging of the follow-up engine
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

async def debug_followup_step_by_step():
    """Debug follow-up engine step by step"""
    
    print("🔍 Deep Debug of Follow-up Engine")
    
    await db_service.connect()
    
    # Import the follow-up engine
    from app.services.smart_follow_up_engine_enhanced import enhanced_smart_follow_up_engine
    
    # Step 1: Get active campaigns
    print("\n1️⃣ Getting active follow-up campaigns...")
    campaigns = await enhanced_db_service.get_active_follow_up_campaigns_enhanced()
    print(f"   Found {len(campaigns)} active campaigns")
    
    if not campaigns:
        print("❌ No active campaigns found")
        return
        
    campaign = campaigns[0]
    campaign_id = campaign["id"]
    print(f"   Campaign: {campaign['name']} (ID: {campaign_id})")
    print(f"   Follow-up intervals: {campaign.get('follow_up_intervals', [])}")
    
    # Step 2: Get prospects needing follow-up
    print("\n2️⃣ Getting prospects needing follow-up...")
    prospects_needing_follow_up = await enhanced_db_service.get_prospects_needing_follow_up_enhanced(campaign_id)
    print(f"   Found {len(prospects_needing_follow_up)} prospects needing follow-up")
    
    if not prospects_needing_follow_up:
        print("❌ No prospects needing follow-up")
        return
        
    prospect = prospects_needing_follow_up[0]
    print(f"   Prospect: {prospect['email']}")
    print(f"   Last contact: {prospect.get('last_contact')}")
    print(f"   Follow-up count: {prospect.get('follow_up_count', 0)}")
    print(f"   Follow-up status: {prospect.get('follow_up_status')}")
    
    # Step 3: Check timing manually
    print("\n3️⃣ Checking timing logic...")
    
    import pytz
    
    # Get campaign timezone
    campaign_timezone = campaign.get("follow_up_timezone", "UTC")
    tz = pytz.timezone(campaign_timezone)
    current_time = datetime.now(tz)
    print(f"   Current time ({campaign_timezone}): {current_time}")
    
    # Check intervals
    follow_up_intervals = campaign.get("follow_up_intervals", [3, 7, 14])
    follow_up_count = prospect.get("follow_up_count", 0)
    
    if follow_up_count < len(follow_up_intervals):
        interval_value = follow_up_intervals[follow_up_count]
    else:
        interval_value = follow_up_intervals[-1]
        
    print(f"   Next interval: {interval_value} {'minutes' if interval_value < 1440 else 'days'}")
    
    # Check time since last contact
    last_contact = prospect.get("last_contact") or prospect.get("created_at")
    if last_contact:
        if last_contact.tzinfo is None:
            reference_time = pytz.UTC.localize(last_contact)
        else:
            reference_time = last_contact
            
        reference_time = reference_time.astimezone(tz)
        time_since_last = current_time - reference_time
        
        if interval_value < 1440:  # Minutes
            minutes_since_last = time_since_last.total_seconds() / 60
            print(f"   Minutes since last contact: {minutes_since_last:.2f}")
            print(f"   Required: >= {interval_value} minutes")
            time_check_passed = minutes_since_last >= interval_value
        else:  # Days
            days_since_last = time_since_last.total_seconds() / (24 * 3600)
            print(f"   Days since last contact: {days_since_last:.2f}")
            print(f"   Required: >= {interval_value / 1440} days")
            time_check_passed = days_since_last >= (interval_value / 1440)
            
        print(f"   Time check passed: {time_check_passed}")
        
        if time_check_passed:
            # Step 4: Check time window
            print("\n4️⃣ Checking time window...")
            current_day = current_time.strftime("%A").lower()
            allowed_days = campaign.get("follow_up_days_of_week", 
                                     ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"])
            
            start_time = campaign.get("follow_up_time_window_start", "00:00")
            end_time = campaign.get("follow_up_time_window_end", "23:59")
            current_time_str = current_time.strftime("%H:%M")
            
            print(f"   Current day: {current_day}")
            print(f"   Allowed days: {allowed_days}")
            print(f"   Current time: {current_time_str}")
            print(f"   Time window: {start_time} - {end_time}")
            
            day_allowed = current_day in allowed_days
            in_time_window = start_time <= current_time_str <= end_time
            
            print(f"   Day allowed: {day_allowed}")
            print(f"   In time window: {in_time_window}")
            
            can_send = day_allowed and in_time_window
            print(f"   Can send now: {can_send}")
            
            if can_send:
                # Step 5: Get email provider
                print("\n5️⃣ Getting email provider...")
                original_provider = await enhanced_db_service.get_prospect_original_provider(prospect["id"])
                if original_provider:
                    print(f"   Provider: {original_provider['name']} (ID: {original_provider['id']})")
                else:
                    print("   ❌ No email provider found")
                    return
                
                # Step 6: Get template
                print("\n6️⃣ Getting follow-up template...")
                template = await enhanced_db_service.get_follow_up_template_for_campaign(campaign_id, follow_up_count + 1)
                if not template:
                    # Fallback to main campaign template
                    template = await db_service.get_template_by_id(campaign.get("template_id"))
                    if template:
                        template["subject"] = f"Follow-up: {template.get('subject', '')}"
                        print(f"   Using main template (modified): {template['name']}")
                    else:
                        print("   ❌ No template found")
                        return
                else:
                    print(f"   Template: {template['name']}")
                
                # Step 7: Try sending email
                print("\n7️⃣ Attempting to send follow-up email...")
                
                from app.services.email_provider_service import email_provider_service
                from app.utils.helpers import personalize_template
                
                # Personalize email content
                personalized_content = personalize_template(template["content"], prospect)
                personalized_subject = personalize_template(template["subject"], prospect)
                
                if follow_up_count > 0:
                    personalized_subject = f"Re: {personalized_subject}"
                    
                print(f"   To: {prospect['email']}")
                print(f"   Subject: {personalized_subject}")
                print(f"   Via provider: {original_provider['name']}")
                
                # Actually try to send
                try:
                    success, error = await email_provider_service.send_email(
                        original_provider["id"], 
                        prospect["email"], 
                        personalized_subject, 
                        personalized_content
                    )
                    
                    print(f"   Send result: {'SUCCESS' if success else 'FAILED'}")
                    if error:
                        print(f"   Error: {error}")
                        
                    if success:
                        print("✅ Email sent successfully! Creating records...")
                        
                        # Create email record
                        email_id = generate_id()
                        email_record = {
                            "id": email_id,
                            "prospect_id": prospect["id"],
                            "campaign_id": campaign_id,
                            "email_provider_id": original_provider["id"],
                            "recipient_email": prospect["email"],
                            "subject": personalized_subject,
                            "content": personalized_content,
                            "status": "sent",
                            "sent_at": datetime.utcnow(),
                            "is_follow_up": True,
                            "follow_up_sequence": follow_up_count + 1,
                            "created_at": datetime.utcnow(),
                            "sent_by_us": True,
                            "thread_id": f"thread_{prospect['id']}",
                            "template_id": template["id"],
                            "provider_name": original_provider["name"]
                        }
                        
                        await db_service.create_email_record(email_record)
                        print("   ✅ Email record created")
                        
                        # Update prospect
                        await enhanced_db_service.mark_follow_up_as_processed(prospect["id"], follow_up_count + 1)
                        print("   ✅ Prospect follow-up tracking updated")
                        
                        print("\n🎉 Follow-up email sent successfully!")
                        
                except Exception as e:
                    print(f"   ❌ Exception during sending: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print("   ❌ Cannot send - outside time window")
        else:
            print("   ❌ Cannot send - not enough time has passed")
    else:
        print("   ❌ No last_contact time found")

if __name__ == "__main__":
    asyncio.run(debug_followup_step_by_step())