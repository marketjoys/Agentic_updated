#!/usr/bin/env python3
"""
Complete Demo Setup for AI Email Responder
Creates all necessary seed data for testing campaign sending, follow-ups, and auto email responders
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from app.services.database import db_service
from app.utils.helpers import generate_id
from datetime import datetime, timedelta

async def setup_email_providers():
    """Create email providers for campaign sending"""
    print("🔧 Setting up email providers...")
    
    providers = [
        {
            "id": generate_id(),
            "name": "Test Gmail Provider",
            "provider_type": "gmail",
            "email_address": "demo@gmail.com",
            "display_name": "Demo Sender",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_username": "demo@gmail.com",
            "smtp_password": "demo_password",
            "smtp_use_tls": True,
            "imap_host": "imap.gmail.com",
            "imap_port": 993,
            "imap_username": "demo@gmail.com",
            "imap_password": "demo_password",
            "imap_use_ssl": True,
            "daily_send_limit": 500,
            "hourly_send_limit": 50,
            "is_active": True,
            "is_default": True,
            "skip_connection_test": True,  # Skip for demo
            "current_daily_count": 0,
            "current_hourly_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_sync": datetime.utcnow()
        }
    ]
    
    for provider in providers:
        await db_service.create_email_provider(provider)
        print(f"✅ Created email provider: {provider['name']}")

async def setup_templates():
    """Create email templates with knowledge base integration"""
    print("📝 Setting up email templates...")
    
    templates = [
        {
            "id": generate_id(),
            "name": "Initial Outreach - Tech Companies",
            "subject": "Partnership opportunity for {{company}}",
            "content": "<p>Hi {{first_name}},</p><p>I hope this email finds you well at {{company}}. I came across your profile and was impressed by your work in the {{industry}} space.</p><p>We've been helping companies like yours streamline their email communication and increase response rates by up to 300%. I'd love to show you how our AI-powered solution could benefit {{company}}.</p><p>Would you be available for a quick 15-minute call this week to discuss?</p><p>Best regards,<br>Demo Team</p>",
            "type": "initial",
            "placeholders": ["first_name", "company", "industry"],
            "knowledge_base_ids": [],
            "use_ai_enhancement": True,
            "ai_enhancement_prompt": "Enhance this email to be more personalized and relevant to the recipient's industry",
            "created_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "name": "Follow-up #1 - Gentle Reminder",
            "subject": "Re: Partnership opportunity for {{company}}",
            "content": "<p>Hi {{first_name}},</p><p>I wanted to follow up on my previous email about helping {{company}} improve email engagement.</p><p>I understand you're probably busy, but I genuinely believe our solution could make a significant impact on your communication strategy.</p><p>Would next week work better for a brief chat?</p><p>Best,<br>Demo Team</p>",
            "type": "follow_up",
            "placeholders": ["first_name", "company", "industry"],
            "knowledge_base_ids": [],
            "use_ai_enhancement": True,
            "ai_enhancement_prompt": "Make this follow-up feel helpful rather than pushy",
            "created_at": datetime.utcnow()
        }
    ]
    
    for template in templates:
        await db_service.create_template(template)
        print(f"✅ Created template: {template['name']}")
    
    return templates

async def setup_prospects():
    """Create prospect data for campaigns"""
    print("👥 Setting up prospects...")
    
    prospects = [
        {
            "id": generate_id(),
            "email": "john.doe@techcorp.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "TechCorp Inc",
            "job_title": "VP of Engineering",
            "industry": "Technology",
            "phone": "+1-555-0101",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "company_domain": "techcorp.com",
            "location": "San Francisco, CA",
            "company_size": "50-200",
            "annual_revenue": "$10M-$50M",
            "lead_source": "LinkedIn",
            "list_ids": [],
            "tags": ["enterprise", "tech"],
            "status": "active",
            "follow_up_status": "active",
            "follow_up_count": 0,
            "created_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "email": "sarah.smith@innovatesoft.com",
            "first_name": "Sarah",
            "last_name": "Smith",
            "company": "InnovateSoft",
            "job_title": "CTO",
            "industry": "Software",
            "phone": "+1-555-0102",
            "linkedin_url": "https://linkedin.com/in/sarahsmith",
            "company_domain": "innovatesoft.com",
            "location": "Austin, TX",
            "company_size": "20-50",
            "annual_revenue": "$1M-$10M",
            "lead_source": "Referral",
            "list_ids": [],
            "tags": ["startup", "software"],
            "status": "active",
            "follow_up_status": "active",
            "follow_up_count": 0,
            "created_at": datetime.utcnow()
        }
    ]
    
    for prospect in prospects:
        await db_service.create_prospect(prospect)
        print(f"✅ Created prospect: {prospect['first_name']} {prospect['last_name']} ({prospect['company']})")
    
    return prospects

async def setup_campaigns(templates, prospects):
    """Create campaigns in draft status to show play button"""
    print("🎯 Setting up campaigns...")
    
    campaigns = [
        {
            "id": generate_id(),
            "name": "Q1 2025 Tech Outreach",
            "template_id": templates[0]["id"],  # Initial Outreach template
            "list_ids": [],
            "prospect_count": len(prospects),
            "max_emails": 1000,
            "email_provider_id": "",  # Will use default
            "schedule_type": "immediate",
            "follow_up_enabled": True,
            "follow_up_intervals": [3, 7, 14],
            "follow_up_templates": [templates[1]["id"]],  # Follow-up template
            "sent_count": 0,
            "delivered_count": 0,
            "opened_count": 0,
            "replied_count": 0,
            "status": "draft",  # IMPORTANT: Draft status to show play button
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": generate_id(),
            "name": "Follow-up Campaign - Week 2",
            "template_id": templates[1]["id"],  # Follow-up template
            "list_ids": [],
            "prospect_count": 2,
            "max_emails": 500,
            "email_provider_id": "",
            "schedule_type": "scheduled",
            "start_time": datetime.utcnow() + timedelta(days=7),
            "follow_up_enabled": False,
            "follow_up_intervals": [],
            "follow_up_templates": [],
            "sent_count": 0,
            "delivered_count": 0,
            "opened_count": 0,
            "replied_count": 0,
            "status": "draft",  # IMPORTANT: Draft status to show play button
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for campaign in campaigns:
        await db_service.create_campaign(campaign)
        print(f"✅ Created campaign: {campaign['name']} (Status: {campaign['status']})")
    
    return campaigns

async def setup_knowledge_base():
    """Create knowledge base articles for AI responder"""
    print("📚 Setting up knowledge base...")
    
    articles = [
        {
            "id": generate_id(),
            "title": "Company Overview and Value Proposition",
            "content": "Our AI Email Responder platform revolutionizes how businesses handle email communication. Key Benefits: Increase email response rates by up to 300%, Automate follow-up sequences intelligently, AI-powered intent classification and response generation.",
            "category": "company_info",
            "tags": ["overview", "value proposition", "benefits"],
            "keywords": ["AI", "email", "automation", "response rates", "analytics"],
            "embedding_vector": [0.1] * 128,
            "relevance_score": 0.0,
            "usage_count": 0,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for article in articles:
        await db_service.create_knowledge_article(article)
        print(f"✅ Created knowledge article: {article['title']}")
    
    return articles

async def main():
    """Main setup function"""
    print("🚀 Starting Complete AI Email Responder Demo Setup...")
    print("=" * 60)
    
    try:
        # Connect to database
        await db_service.connect()
        print("✅ Connected to database")
        
        # Setup all components
        await setup_email_providers()
        templates = await setup_templates()
        prospects = await setup_prospects()
        campaigns = await setup_campaigns(templates, prospects)
        articles = await setup_knowledge_base()
        
        print("\n" + "=" * 60)
        print("🎉 COMPLETE DEMO SETUP SUCCESSFUL!")
        print("=" * 60)
        print(f"✅ Email Providers: 1 created (default)")
        print(f"✅ Templates: {len(templates)} created")
        print(f"✅ Prospects: {len(prospects)} created")
        print(f"✅ Campaigns: {len(campaigns)} created (draft status)")
        print(f"✅ Knowledge Base: {len(articles)} articles created")
        
        print("\n🎯 WHAT'S NOW AVAILABLE:")
        print("1. 📧 CAMPAIGN SENDING: Play buttons visible on draft campaigns")
        print("2. 🔄 FOLLOW-UP ENGINE: Smart follow-up configuration ready")
        print("3. 🤖 AUTO EMAIL RESPONDER: Knowledge base ready for AI responses")
        print("4. 👥 PROSPECTS: Realistic prospects for testing")
        
        print("\n🧪 READY TO TEST:")
        print("• Login to frontend and navigate to Campaigns")
        print("• Click play button on draft campaigns to send emails") 
        print("• Go to Email Processing to start AI responder")
        print("• Check Knowledge Base for AI training content")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await db_service.disconnect()
        print("\n✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(main())