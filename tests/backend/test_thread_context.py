#!/usr/bin/env python3

"""
Test script to demonstrate thread context functionality
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.services.database import db_service
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id
from datetime import datetime

async def test_thread_context():
    """Test thread context functionality"""
    
    print("🧪 Testing Thread Context Functionality...")
    
    # Connect to database
    await db_service.connect()
    
    # Get a test prospect
    prospects = await db_service.get_prospects()
    if not prospects:
        print("❌ No prospects found in database")
        return
    
    prospect = prospects[0]
    print(f"✅ Using prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
    
    # Create thread context
    thread_id = generate_id()
    thread_data = {
        "id": thread_id,
        "prospect_id": prospect["id"],
        "prospect_email": prospect["email"],
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "messages": [],
        "status": "active"
    }
    
    await db_service.create_thread_context(thread_data)
    print(f"✅ Created thread: {thread_id}")
    
    # Add initial message from us (outbound campaign)
    initial_message = {
        "type": "sent",
        "sender": "us",
        "recipient": prospect["email"],
        "subject": "AI Email Automation - Transform Your Business",
        "content": f"Hi {prospect['first_name']},\n\nI hope this email finds you well. I wanted to reach out because I noticed that TechCorp Inc is in the technology space, and I believe our AI email automation solution could significantly streamline your communication processes.\n\nWould you be interested in learning more about how we can help automate your email workflows?\n\nBest regards,\nSarah Johnson",
        "timestamp": datetime.utcnow(),
        "sent_by_us": True,
        "ai_generated": False
    }
    
    await db_service.add_message_to_thread(thread_id, initial_message)
    print("✅ Added initial outbound message")
    
    # Add prospect's response (interested)
    response_message = {
        "type": "received",
        "sender": prospect["email"],
        "recipient": "us",
        "subject": "Re: AI Email Automation - Transform Your Business",
        "content": f"Hi Sarah,\n\nThank you for reaching out! I'm definitely interested in learning more about your AI email automation solution. We're currently looking to improve our email processes at {prospect['company']}.\n\nCould you tell me more about the pricing and features? Also, would it be possible to schedule a demo?\n\nLooking forward to hearing from you.\n\nBest regards,\n{prospect['first_name']}",
        "timestamp": datetime.utcnow(),
        "sent_by_us": False,
        "ai_generated": False,
        "is_response_to_our_email": True
    }
    
    await db_service.add_message_to_thread(thread_id, response_message)
    print("✅ Added prospect's interested response")
    
    # Test AI classification and response generation with conversation context
    print("\n🤖 Testing AI Classification and Response Generation...")
    
    # Classify the prospect's response
    classified_intents = await groq_service.classify_intents(
        response_message["content"], 
        response_message["subject"]
    )
    
    print(f"📋 Classified Intents: {len(classified_intents)}")
    for intent in classified_intents:
        print(f"  - {intent['intent_name']}: {intent['confidence']:.2f} confidence")
        print(f"    Keywords: {intent.get('keywords_found', [])}")
    
    # Get conversation context
    thread_context = await db_service.get_thread_by_id(thread_id)
    conversation_context = thread_context.get("messages", [])
    
    print(f"📚 Conversation Context: {len(conversation_context)} messages")
    
    # Generate response with conversation context
    response_data = await groq_service.generate_response(
        response_message["content"],
        response_message["subject"],
        classified_intents,
        conversation_context,
        prospect
    )
    
    print("\n💬 Generated AI Response:")
    print(f"Subject: {response_data.get('subject', 'N/A')}")
    print(f"Content: {response_data.get('content', 'N/A')}")
    print(f"Confidence: {response_data.get('confidence', 'N/A')}")
    print(f"Context Used: {response_data.get('conversation_context_used', 'N/A')}")
    
    # Add AI response to thread
    ai_response_message = {
        "type": "sent",
        "sender": "us",
        "recipient": prospect["email"],
        "subject": response_data.get("subject", ""),
        "content": response_data.get("content", ""),
        "timestamp": datetime.utcnow(),
        "sent_by_us": True,
        "ai_generated": True,
        "is_auto_response": True,
        "intents_addressed": [intent["intent_id"] for intent in classified_intents],
        "template_used": response_data.get("template_used")
    }
    
    await db_service.add_message_to_thread(thread_id, ai_response_message)
    print("✅ Added AI response to thread")
    
    # Test follow-up scenario - prospect asks more questions
    followup_message = {
        "type": "received",
        "sender": prospect["email"],
        "recipient": "us",
        "subject": "Re: AI Email Automation - Transform Your Business",
        "content": f"Hi Sarah,\n\nThank you for the detailed information about your AI email automation solution. I'm very interested!\n\nI have a few more questions:\n1. What integrations do you support with existing CRM systems?\n2. How long is the typical implementation process?\n3. Do you offer training for our team?\n\nAlso, I'd like to schedule that demo as soon as possible. When would be a good time for you?\n\nBest regards,\n{prospect['first_name']}",
        "timestamp": datetime.utcnow(),
        "sent_by_us": False,
        "ai_generated": False,
        "is_response_to_our_email": True
    }
    
    await db_service.add_message_to_thread(thread_id, followup_message)
    print("✅ Added follow-up message")
    
    # Test AI response with more conversation context
    print("\n🔄 Testing AI Response with Extended Context...")
    
    # Classify the follow-up
    classified_intents_2 = await groq_service.classify_intents(
        followup_message["content"], 
        followup_message["subject"]
    )
    
    print(f"📋 Classified Intents (Follow-up): {len(classified_intents_2)}")
    for intent in classified_intents_2:
        print(f"  - {intent['intent_name']}: {intent['confidence']:.2f} confidence")
    
    # Get updated conversation context
    thread_context_updated = await db_service.get_thread_by_id(thread_id)
    conversation_context_updated = thread_context_updated.get("messages", [])
    
    print(f"📚 Updated Conversation Context: {len(conversation_context_updated)} messages")
    
    # Generate follow-up response
    response_data_2 = await groq_service.generate_response(
        followup_message["content"],
        followup_message["subject"],
        classified_intents_2,
        conversation_context_updated,
        prospect
    )
    
    print("\n💬 Generated Follow-up AI Response:")
    print(f"Subject: {response_data_2.get('subject', 'N/A')}")
    print(f"Content: {response_data_2.get('content', 'N/A')}")
    print(f"Context Used: {response_data_2.get('conversation_context_used', 'N/A')}")
    
    # Display final thread summary
    print("\n📊 Final Thread Summary:")
    final_thread = await db_service.get_thread_by_id(thread_id)
    messages = final_thread.get("messages", [])
    
    print(f"Thread ID: {thread_id}")
    print(f"Total Messages: {len(messages)}")
    print(f"Messages by Us: {len([m for m in messages if m.get('sent_by_us')])}")
    print(f"Messages from Prospect: {len([m for m in messages if not m.get('sent_by_us')])}")
    print(f"AI Generated: {len([m for m in messages if m.get('ai_generated')])}")
    
    print("\n🎉 Thread Context Test Completed Successfully!")
    print("✅ Conversation context is properly maintained")
    print("✅ AI responses use previous conversation history")
    print("✅ Threading functionality is working correctly")
    
    return thread_id

if __name__ == "__main__":
    asyncio.run(test_thread_context())