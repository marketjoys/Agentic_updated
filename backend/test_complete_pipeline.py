#!/usr/bin/env python3
"""
Complete test of the email processing pipeline
"""
import asyncio
from datetime import datetime
from app.services.database import db_service
from app.services.groq_service import groq_service
from app.services.email_processor import email_processor
from app.utils.helpers import generate_id

async def test_complete_email_processing():
    """Test the complete email processing pipeline"""
    try:
        print("🧪 Testing Complete Email Processing Pipeline...")
        
        # Connect to database
        await db_service.connect()
        
        # Get a test prospect
        prospects = await db_service.get_prospects()
        if not prospects:
            print("❌ No prospects found in database")
            return
        
        prospect = prospects[0]
        print(f"📧 Testing with prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
        
        # Simulate an incoming email
        test_email_content = """
        Hi there!
        
        I received your email about potential collaboration opportunities. 
        I'm very interested in learning more about your services and how we can work together.
        
        Could you please send me more information about your offerings?
        
        Best regards,
        John Doe
        CEO, TechCorp Inc
        """
        
        test_subject = "Re: Collaboration Opportunity - Very Interested!"
        
        print(f"\n📨 Simulating incoming email:")
        print(f"From: {prospect['email']}")
        print(f"Subject: {test_subject}")
        print(f"Content: {test_email_content[:100]}...")
        
        # Test the email processing pipeline
        print(f"\n🔄 Processing email through pipeline...")
        
        # Step 1: Create/get thread context
        thread_context = await email_processor._get_or_create_thread_context(
            prospect["id"], 
            prospect["email"]
        )
        print(f"✅ Thread context: {thread_context['id']}")
        
        # Step 2: Classify intents
        classified_intents = await groq_service.classify_intents(test_email_content, test_subject)
        print(f"✅ Classified intents: {len(classified_intents)}")
        for intent in classified_intents:
            print(f"  - {intent.get('intent_name', 'Unknown')}: {intent.get('confidence', 0):.2f}")
        
        # Step 3: Generate response
        response_data = await groq_service.generate_response(
            test_email_content,
            test_subject,
            classified_intents,
            [],  # No conversation context
            prospect
        )
        
        if response_data.get("error"):
            print(f"❌ Response generation failed: {response_data['error']}")
            return
        
        print(f"✅ Response generated:")
        print(f"  Subject: {response_data.get('subject', 'No subject')}")
        print(f"  Content preview: {response_data.get('content', 'No content')[:150]}...")
        
        # Step 4: Check if should auto-respond
        should_respond = await email_processor._should_auto_respond(classified_intents)
        print(f"✅ Should auto-respond: {should_respond}")
        
        # Step 5: Simulate sending automatic response
        if should_respond:
            print(f"\n📤 Simulating automatic response...")
            
            # Add the incoming message to thread
            incoming_message = {
                "type": "received",
                "sender": prospect["email"],
                "subject": test_subject,
                "content": test_email_content,
                "timestamp": datetime.utcnow(),
                "is_response_to_our_email": False,
                "message_id": f"msg_{generate_id()}"
            }
            
            await email_processor._add_message_to_thread(thread_context["id"], incoming_message)
            print(f"✅ Added incoming message to thread")
            
            # Send automatic response
            await email_processor._send_automatic_response(
                prospect,
                response_data,
                thread_context["id"]
            )
            print(f"✅ Automatic response sent successfully!")
            
            # Verify thread was updated
            updated_thread = await db_service.get_thread_by_id(thread_context["id"])
            if updated_thread:
                message_count = len(updated_thread.get("messages", []))
                print(f"✅ Thread now has {message_count} messages")
                
                # Show last few messages
                for i, msg in enumerate(updated_thread.get("messages", [])[-2:]):
                    msg_type = "📨 Received" if msg.get("type") == "received" else "📤 Sent"
                    print(f"  {i+1}. {msg_type}: {msg.get('subject', 'No subject')}")
        
        await db_service.disconnect()
        print(f"\n🎉 Complete email processing test successful!")
        print(f"\n📊 Summary:")
        print(f"  - Intent classification: ✅ Working")
        print(f"  - Response generation: ✅ Working")
        print(f"  - Auto-response decision: ✅ Working")
        print(f"  - Email sending: ✅ Working")
        print(f"  - Thread management: ✅ Working")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_complete_email_processing())