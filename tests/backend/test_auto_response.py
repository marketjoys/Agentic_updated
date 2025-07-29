#!/usr/bin/env python3
"""
Test script for automatic email response functionality
"""
import asyncio
from app.services.database import db_service
from app.services.groq_service import groq_service
from app.services.email_processor import email_processor

async def test_automatic_response():
    """Test the automatic response flow"""
    try:
        print("🧪 Testing Automatic Email Response Flow...")
        
        # Connect to database
        await db_service.connect()
        
        # Test 1: Check if intents are configured for auto-response
        print("\n📋 Step 1: Checking intent configuration...")
        intents = await db_service.get_intents()
        print(f"Found {len(intents)} intents:")
        for intent in intents:
            auto_respond = intent.get("auto_respond", False)
            print(f"  - {intent['name']}: auto_respond = {auto_respond}")
        
        # Test 2: Test intent classification
        print("\n🤖 Step 2: Testing intent classification...")
        test_email_content = "Hi! I'm very interested in your proposal. Please tell me more about your services."
        test_subject = "Re: Your proposal sounds great!"
        
        classified_intents = await groq_service.classify_intents(test_email_content, test_subject)
        print(f"Classified intents: {len(classified_intents)}")
        for intent in classified_intents:
            print(f"  - {intent.get('intent_name', 'Unknown')}: {intent.get('confidence', 0):.2f}")
        
        # Test 3: Test response generation
        print("\n📝 Step 3: Testing response generation...")
        if classified_intents:
            # Get a sample prospect
            prospects = await db_service.get_prospects()
            if prospects:
                prospect = prospects[0]
                print(f"Using prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
                
                response_data = await groq_service.generate_response(
                    test_email_content, 
                    test_subject, 
                    classified_intents,
                    [],  # No conversation context
                    prospect
                )
                
                if response_data.get("error"):
                    print(f"❌ Response generation failed: {response_data['error']}")
                else:
                    print(f"✅ Response generated successfully")
                    print(f"  Subject: {response_data.get('subject', 'No subject')}")
                    print(f"  Content preview: {response_data.get('content', 'No content')[:100]}...")
        
        # Test 4: Test auto-response decision
        print("\n🎯 Step 4: Testing auto-response decision...")
        should_respond = await email_processor._should_auto_respond(classified_intents)
        print(f"Should auto-respond: {should_respond}")
        
        await db_service.disconnect()
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        await db_service.disconnect()

if __name__ == "__main__":
    asyncio.run(test_automatic_response())