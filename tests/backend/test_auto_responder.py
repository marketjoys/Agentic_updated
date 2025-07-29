#!/usr/bin/env python3

"""
Test script to verify automatic responder functionality and AI context access
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.services.database import db_service
from app.services.email_processor import email_processor
from app.services.groq_service import groq_service
from app.utils.helpers import generate_id
from datetime import datetime
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

async def test_automatic_responder():
    """Test the complete automatic responder workflow"""
    
    print("🧪 Testing Automatic Responder Functionality...")
    
    # Connect to database
    await db_service.connect()
    
    # Get existing prospect
    prospects = await db_service.get_prospects()
    prospect = prospects[0]
    print(f"✅ Using prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['email']})")
    
    # Create a mock incoming email message
    print("\n📧 Creating mock incoming email...")
    
    mock_email = MIMEMultipart()
    mock_email["From"] = f"{prospect['first_name']} {prospect['last_name']} <{prospect['email']}>"
    mock_email["To"] = "sarah@company.com"
    mock_email["Subject"] = "Re: AI Email Automation - Very Interested!"
    mock_email["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    
    email_content = f"""Hi Sarah,

Thank you for reaching out about your AI email automation solution. I've reviewed the information and I'm very interested in proceeding.

I have a few questions:
1. What's the pricing for a team of 50 users?
2. Do you offer integration with Salesforce?
3. Can we schedule a demo for next week?

I'm ready to move forward with this solution as it looks like exactly what we need at {prospect['company']}.

Best regards,
{prospect['first_name']} {prospect['last_name']}
{prospect['job_title']}
{prospect['company']}"""
    
    mock_email.attach(MIMEText(email_content, "plain"))
    
    print(f"✅ Created mock email from: {prospect['email']}")
    print(f"Subject: {mock_email['Subject']}")
    print(f"Content preview: {email_content[:100]}...")
    
    # Test email processing directly
    print("\n🔄 Processing email through email processor...")
    
    # Process the email (this will test the complete flow)
    result = await email_processor._process_email(mock_email)
    
    if result:
        print("✅ Email processed successfully")
    else:
        print("❌ Email processing failed")
        return False
    
    # Check if thread was created/updated
    print("\n🧵 Checking thread creation...")
    
    thread = await db_service.get_thread_by_prospect_id(prospect["id"])
    if thread:
        print(f"✅ Thread found: {thread['id']}")
        print(f"Total messages in thread: {len(thread.get('messages', []))}")
        
        # Show messages in thread
        messages = thread.get('messages', [])
        for i, msg in enumerate(messages):
            msg_type = "📤 SENT" if msg.get('sent_by_us') else "📥 RECEIVED"
            ai_flag = " (AI)" if msg.get('ai_generated') else ""
            print(f"  {i+1}. {msg_type}{ai_flag}: {msg.get('subject', 'No subject')}")
    else:
        print("❌ No thread found")
        return False
    
    # Test AI classification with context
    print("\n🤖 Testing AI classification with context...")
    
    classified_intents = await groq_service.classify_intents(email_content, mock_email["Subject"])
    print(f"📋 Classified {len(classified_intents)} intents:")
    
    for intent in classified_intents:
        print(f"  - {intent['intent_name']}: {intent['confidence']:.2f} confidence")
        print(f"    Keywords: {intent.get('keywords_found', [])}")
        print(f"    Reasoning: {intent.get('reasoning', 'N/A')}")
    
    # Test response generation with conversation context
    print("\n💬 Testing response generation with conversation context...")
    
    # Get updated conversation context
    conversation_context = thread.get('messages', [])
    
    print(f"📚 Using conversation context: {len(conversation_context)} messages")
    
    # Generate response
    response_data = await groq_service.generate_response(
        email_content,
        mock_email["Subject"],
        classified_intents,
        conversation_context,
        prospect
    )
    
    if response_data.get("error"):
        print(f"❌ Response generation failed: {response_data['error']}")
        return False
    
    print("✅ Response generated successfully!")
    print(f"Subject: {response_data.get('subject', 'N/A')}")
    print(f"Content preview: {response_data.get('content', 'N/A')[:200]}...")
    print(f"Conversation context used: {response_data.get('conversation_context_used', 'N/A')}")
    print(f"Confidence: {response_data.get('confidence', 'N/A')}")
    
    # Test auto-response decision
    print("\n🎯 Testing auto-response decision...")
    
    should_respond = await email_processor._should_auto_respond(classified_intents)
    print(f"Should auto-respond: {should_respond}")
    
    if should_respond:
        print("✅ Auto-response criteria met")
    else:
        print("ℹ️  Auto-response criteria not met")
    
    # Check if email record was created
    print("\n📊 Checking email records...")
    
    # Get all emails for this prospect
    emails = await db_service.db.emails.find({"prospect_id": prospect["id"]}).to_list(length=100)
    
    print(f"Found {len(emails)} email records for prospect")
    
    for email_record in emails:
        status = email_record.get("status", "unknown")
        ai_flag = " (AI)" if email_record.get("ai_generated") else ""
        auto_flag = " (AUTO)" if email_record.get("is_auto_response") else ""
        print(f"  - {status.upper()}{ai_flag}{auto_flag}: {email_record.get('subject', 'No subject')}")
    
    # Test with different email types
    print("\n🔄 Testing with different email types...")
    
    # Test "Not Interested" email
    print("\n📧 Testing 'Not Interested' email...")
    
    not_interested_email = MIMEMultipart()
    not_interested_email["From"] = f"{prospect['first_name']} {prospect['last_name']} <{prospect['email']}>"
    not_interested_email["To"] = "sarah@company.com"
    not_interested_email["Subject"] = "Re: AI Email Automation - Not Interested"
    
    not_interested_content = f"""Hi Sarah,

Thank you for reaching out about your AI email automation solution.

I appreciate the information, but we're not interested in this type of solution at this time. We have other priorities right now.

Please remove me from your mailing list.

Best regards,
{prospect['first_name']}"""
    
    not_interested_email.attach(MIMEText(not_interested_content, "plain"))
    
    # Classify the "not interested" email
    not_interested_intents = await groq_service.classify_intents(
        not_interested_content, 
        not_interested_email["Subject"]
    )
    
    print(f"📋 'Not Interested' email classified as:")
    for intent in not_interested_intents:
        print(f"  - {intent['intent_name']}: {intent['confidence']:.2f} confidence")
    
    # Test response generation for "not interested"
    not_interested_response = await groq_service.generate_response(
        not_interested_content,
        not_interested_email["Subject"],
        not_interested_intents,
        conversation_context,
        prospect
    )
    
    print(f"💬 'Not Interested' response generated:")
    print(f"Subject: {not_interested_response.get('subject', 'N/A')}")
    print(f"Content preview: {not_interested_response.get('content', 'N/A')[:150]}...")
    
    # Test final thread state
    print("\n📊 Final thread analysis...")
    
    final_thread = await db_service.get_thread_by_prospect_id(prospect["id"])
    if final_thread:
        messages = final_thread.get('messages', [])
        print(f"Final thread has {len(messages)} messages:")
        
        sent_by_us = len([m for m in messages if m.get('sent_by_us')])
        received_from_prospect = len([m for m in messages if not m.get('sent_by_us')])
        ai_generated = len([m for m in messages if m.get('ai_generated')])
        auto_responses = len([m for m in messages if m.get('is_auto_response')])
        
        print(f"  - Sent by us: {sent_by_us}")
        print(f"  - Received from prospect: {received_from_prospect}")
        print(f"  - AI generated: {ai_generated}")
        print(f"  - Auto responses: {auto_responses}")
    
    print("\n🎉 Automatic Responder Test Complete!")
    
    return True

async def test_context_access():
    """Test AI's access to conversation context"""
    
    print("\n🧠 Testing AI Context Access...")
    
    # Get existing thread
    prospects = await db_service.get_prospects()
    prospect = prospects[0]
    
    thread = await db_service.get_thread_by_prospect_id(prospect["id"])
    if not thread:
        print("❌ No thread found for context testing")
        return False
    
    conversation_context = thread.get('messages', [])
    
    # Test AI's ability to reference previous messages
    print(f"📚 Testing with {len(conversation_context)} messages of context")
    
    # Create a follow-up question that requires context
    followup_content = f"""Hi Sarah,

I was reviewing our previous conversation about the AI email automation solution. You mentioned pricing would be based on the number of users.

Could you clarify what you meant by "level of customization"? And what specific features are included in the basic plan versus the premium plan?

Also, regarding the demo we discussed - I'm available Tuesday or Wednesday next week. Would either of those work for you?

Thanks,
{prospect['first_name']}"""
    
    # Classify and generate response
    intents = await groq_service.classify_intents(followup_content, "Re: Follow-up Questions")
    
    response_with_context = await groq_service.generate_response(
        followup_content,
        "Re: Follow-up Questions",
        intents,
        conversation_context,
        prospect
    )
    
    print("✅ Response generated with context:")
    print(f"Context used: {response_with_context.get('conversation_context_used', 'N/A')}")
    print(f"Confidence: {response_with_context.get('confidence', 'N/A')}")
    
    # Check if response references previous conversation
    response_content = response_with_context.get('content', '').lower()
    context_indicators = [
        'previous', 'earlier', 'discussed', 'mentioned', 'conversation', 
        'demo', 'pricing', 'features', 'as we talked about'
    ]
    
    context_references = [indicator for indicator in context_indicators if indicator in response_content]
    
    print(f"📝 Context references found: {context_references}")
    
    if context_references:
        print("✅ AI is successfully referencing previous conversation")
    else:
        print("⚠️  AI may not be fully utilizing conversation context")
    
    # Test without context (for comparison)
    print("\n🔄 Testing same email WITHOUT context (for comparison)...")
    
    response_without_context = await groq_service.generate_response(
        followup_content,
        "Re: Follow-up Questions",
        intents,
        [],  # Empty context
        prospect
    )
    
    print("Response without context:")
    print(f"Context used: {response_without_context.get('conversation_context_used', 'N/A')}")
    print(f"Confidence: {response_without_context.get('confidence', 'N/A')}")
    
    # Compare responses
    with_context_length = len(response_with_context.get('content', ''))
    without_context_length = len(response_without_context.get('content', ''))
    
    print(f"\n📊 Context Impact Analysis:")
    print(f"  - With context: {with_context_length} characters")
    print(f"  - Without context: {without_context_length} characters")
    print(f"  - Difference: {with_context_length - without_context_length} characters")
    
    if with_context_length > without_context_length:
        print("✅ Context provides more detailed responses")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_automatic_responder())
    asyncio.run(test_context_access())