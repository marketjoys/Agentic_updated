#!/usr/bin/env python3
"""
Database Setup and Seeding Script for AI Email Responder
This script creates the MongoDB database and seeds it with test data
"""

import os
import sys
import pymongo
from pymongo import MongoClient
from datetime import datetime
import uuid

def print_status(message):
    print(f"[INFO] {message}")

def print_success(message):
    print(f"[SUCCESS] {message}")

def print_error(message):
    print(f"[ERROR] {message}")

def setup_database():
    """Set up MongoDB database with test data"""
    
    # MongoDB connection
    try:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017/email_responder')
        print_status(f"Connecting to MongoDB: {mongo_url}")
        
        client = MongoClient(mongo_url)
        db = client.get_default_database()
        
        # Test connection
        client.admin.command('ping')
        print_success("MongoDB connection established")
        
    except Exception as e:
        print_error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # Create collections and seed data
    try:
        # Users collection (for test user)
        users_collection = db.users
        
        # Check if test user exists
        test_user = users_collection.find_one({"username": "testuser"})
        if not test_user:
            print_status("Creating test user...")
            test_user_data = {
                "_id": str(uuid.uuid4()),
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password_hash": "$2b$12$dummy.hash.for.testing.only",  # In real app, this would be properly hashed
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            users_collection.insert_one(test_user_data)
            print_success("Test user created")
        else:
            print_success("Test user already exists")
        
        # Prospects collection
        prospects_collection = db.prospects
        if prospects_collection.count_documents({}) == 0:
            print_status("Seeding prospects collection...")
            prospects_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "email": "john.doe@techstartup.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "company": "TechStartup Inc",
                    "job_title": "CEO",
                    "industry": "Technology",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "email": "jane.smith@financegroup.com",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "company": "Finance Group LLC",
                    "job_title": "CFO",
                    "industry": "Finance",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "email": "mike.johnson@healthcorp.com",
                    "first_name": "Mike",
                    "last_name": "Johnson",
                    "company": "Health Corp",
                    "job_title": "Director of Operations",
                    "industry": "Healthcare",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "email": "sarah.wilson@edutech.com",
                    "first_name": "Sarah",
                    "last_name": "Wilson",
                    "company": "EduTech Solutions",
                    "job_title": "VP of Marketing",
                    "industry": "Education",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "email": "david.brown@retailplus.com",
                    "first_name": "David",
                    "last_name": "Brown",
                    "company": "RetailPlus Inc",
                    "job_title": "Operations Manager",
                    "industry": "Retail",
                    "status": "active",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            prospects_collection.insert_many(prospects_data)
            print_success(f"Seeded {len(prospects_data)} prospects")
        
        # Templates collection
        templates_collection = db.templates
        if templates_collection.count_documents({}) == 0:
            print_status("Seeding templates collection...")
            templates_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Welcome Email",
                    "subject": "Welcome to Our Service, {{first_name}}!",
                    "content": "Hello {{first_name}},\n\nWelcome to our service! We're excited to have {{company}} as part of our community.\n\nBest regards,\nThe Team",
                    "type": "initial",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Follow-up Day 3",
                    "subject": "Quick follow-up regarding {{company}}",
                    "content": "Hi {{first_name}},\n\nI wanted to follow up on our previous conversation about {{company}}. I believe our solution could really help with your {{industry}} challenges.\n\nWould you be available for a quick 15-minute call this week?\n\nBest regards,\nThe Team",
                    "type": "follow_up",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Follow-up Day 7",
                    "subject": "Final follow-up for {{company}}",
                    "content": "Hi {{first_name}},\n\nThis is my final follow-up regarding our discussion about {{company}}. I understand you're busy, but I wanted to ensure you had all the information you need.\n\nIf you're interested in learning more, please don't hesitate to reach out.\n\nBest regards,\nThe Team",
                    "type": "follow_up",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Product Demo Invitation",
                    "subject": "See {{company}}'s productivity increase by 40%",
                    "content": "Hello {{first_name}},\n\nI hope this email finds you well. I wanted to reach out because I noticed {{company}} is in the {{industry}} sector, and we've helped similar companies increase their productivity by up to 40%.\n\nWould you be interested in a quick demo to see how this could work for {{company}}?\n\nI have a few slots available this week:\n- Tuesday 2:00 PM\n- Wednesday 10:00 AM\n- Thursday 3:00 PM\n\nLet me know what works best for you!\n\nBest regards,\nThe Team",
                    "type": "initial",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            templates_collection.insert_many(templates_data)
            print_success(f"Seeded {len(templates_data)} templates")
        
        # Campaigns collection
        campaigns_collection = db.campaigns
        if campaigns_collection.count_documents({}) == 0:
            print_status("Seeding campaigns collection...")
            campaigns_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Q1 Outreach Campaign",
                    "status": "draft",
                    "template_id": None,
                    "prospect_count": 5,
                    "max_emails": 1000,
                    "emails_sent": 0,
                    "emails_opened": 0,
                    "emails_replied": 0,
                    "schedule_type": "immediate",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Product Demo Series",
                    "status": "active",
                    "template_id": None,
                    "prospect_count": 3,
                    "max_emails": 500,
                    "emails_sent": 12,
                    "emails_opened": 8,
                    "emails_replied": 2,
                    "schedule_type": "scheduled",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            campaigns_collection.insert_many(campaigns_data)
            print_success(f"Seeded {len(campaigns_data)} campaigns")
        
        # Intents collection
        intents_collection = db.intents
        if intents_collection.count_documents({}) == 0:
            print_status("Seeding intents collection...")
            intents_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Interested",
                    "description": "Prospect shows interest in our service",
                    "keywords": ["interested", "yes", "tell me more", "sounds good", "demo", "schedule"],
                    "auto_respond": True,
                    "response_template": "Thank you for your interest! I'll send you a calendar link to schedule a demo.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Not Interested",
                    "description": "Prospect is not interested",
                    "keywords": ["not interested", "no thanks", "remove me", "unsubscribe", "not right now"],
                    "auto_respond": True,
                    "response_template": "I understand. I'll remove you from our outreach list. Thank you for your time.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Request More Info",
                    "description": "Prospect wants more information",
                    "keywords": ["more info", "details", "pricing", "features", "how it works"],
                    "auto_respond": True,
                    "response_template": "I'd be happy to provide more details! I'll send you our product information sheet.",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Out of Office",
                    "description": "Prospect is out of office",
                    "keywords": ["out of office", "vacation", "away", "back on", "returning"],
                    "auto_respond": False,
                    "response_template": "",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            intents_collection.insert_many(intents_data)
            print_success(f"Seeded {len(intents_data)} intents")
        
        # Lists collection
        lists_collection = db.lists
        if lists_collection.count_documents({}) == 0:
            print_status("Seeding lists collection...")
            lists_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Tech Startups",
                    "description": "Technology startup companies",
                    "color": "#3B82F6",
                    "prospect_count": 2,
                    "tags": ["tech", "startup", "b2b"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Finance Companies",
                    "description": "Financial services companies",
                    "color": "#10B981",
                    "prospect_count": 1,
                    "tags": ["finance", "services", "b2b"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Healthcare Organizations",
                    "description": "Healthcare and medical organizations",
                    "color": "#EF4444",
                    "prospect_count": 1,
                    "tags": ["healthcare", "medical", "b2b"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Education Sector",
                    "description": "Educational institutions and EdTech companies",
                    "color": "#8B5CF6",
                    "prospect_count": 1,
                    "tags": ["education", "edtech", "b2b"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            lists_collection.insert_many(lists_data)
            print_success(f"Seeded {len(lists_data)} lists")
        
        # Email providers collection
        email_providers_collection = db.email_providers
        if email_providers_collection.count_documents({}) == 0:
            print_status("Seeding email providers collection...")
            providers_data = [
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Test Gmail Provider",
                    "provider_type": "gmail",
                    "email_address": "test@gmail.com",
                    "display_name": "Test User",
                    "is_active": True,
                    "is_default": True,
                    "daily_send_limit": 500,
                    "hourly_send_limit": 50,
                    "current_daily_count": 0,
                    "current_hourly_count": 0,
                    "last_sync": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                {
                    "_id": str(uuid.uuid4()),
                    "name": "Test Outlook Provider",
                    "provider_type": "outlook",
                    "email_address": "test@outlook.com",
                    "display_name": "Test User",
                    "is_active": True,
                    "is_default": False,
                    "daily_send_limit": 300,
                    "hourly_send_limit": 30,
                    "current_daily_count": 0,
                    "current_hourly_count": 0,
                    "last_sync": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            ]
            email_providers_collection.insert_many(providers_data)
            print_success(f"Seeded {len(providers_data)} email providers")
        
        # Create indexes for better performance
        print_status("Creating database indexes...")
        
        # Users indexes
        users_collection.create_index("username", unique=True)
        users_collection.create_index("email", unique=True)
        
        # Prospects indexes
        prospects_collection.create_index("email", unique=True)
        prospects_collection.create_index("status")
        prospects_collection.create_index("industry")
        
        # Templates indexes
        templates_collection.create_index("name")
        templates_collection.create_index("type")
        
        # Campaigns indexes
        campaigns_collection.create_index("name")
        campaigns_collection.create_index("status")
        
        # Intents indexes
        intents_collection.create_index("name")
        
        # Lists indexes
        lists_collection.create_index("name")
        
        # Email providers indexes
        email_providers_collection.create_index("email_address")
        email_providers_collection.create_index("provider_type")
        
        print_success("Database indexes created")
        
        # Print summary
        print_success("Database setup completed successfully!")
        print_status("Database Summary:")
        print(f"   Users: {users_collection.count_documents({})}")
        print(f"   Prospects: {prospects_collection.count_documents({})}")
        print(f"   Templates: {templates_collection.count_documents({})}")
        print(f"   Campaigns: {campaigns_collection.count_documents({})}")
        print(f"   Intents: {intents_collection.count_documents({})}")
        print(f"   Lists: {lists_collection.count_documents({})}")
        print(f"   Email Providers: {email_providers_collection.count_documents({})}")
        
        client.close()
        
    except Exception as e:
        print_error(f"Failed to setup database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()