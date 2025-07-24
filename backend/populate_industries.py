#!/usr/bin/env python3
"""
Populate comprehensive industry data for AI Agent
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.database import db_service
from app.utils.helpers import generate_id
from datetime import datetime

async def populate_comprehensive_industries():
    """Populate comprehensive industry data for AI Agent"""
    try:
        await db_service.connect()
        
        # Comprehensive industry list from continuation request
        comprehensive_industries = [
            {"industry": "Accounting", "external_id": "5567ce1f7369643b78570000"},
            {"industry": "Agriculture", "external_id": "55718f947369642142b84a12"},
            {"industry": "Airlines/Aviation", "external_id": "5567e0bf7369641d115f0200"},
            {"industry": "Alternative Dispute Resolution", "external_id": "5567e1a87369641f6d550100"},
            {"industry": "Alternative Medicine", "external_id": "5567e27c7369642ade490000"},
            {"industry": "Animation", "external_id": "5567e36f73696431a4970000"},
            {"industry": "Apparel & Fashion", "external_id": "5567cd82736964540d0b0000"},
            {"industry": "Architecture & Planning", "external_id": "5567cdb77369645401080000"},
            {"industry": "Arts & Crafts", "external_id": "5567cd4d73696439d9030000"},
            {"industry": "Automotive", "external_id": "5567cdf27369644cfd800000"},
            {"industry": "Aviation & Aerospace", "external_id": "5567e0dd73696416d3c20100"},
            {"industry": "Banking", "external_id": "5567ce237369644ee5490000"},
            {"industry": "Biotechnology", "external_id": "5567d08e7369645dbc4b0000"},
            {"industry": "Broadcast Media", "external_id": "5567e0f973696416d34e0200"},
            {"industry": "Building Materials", "external_id": "5567e1a17369641ea9d30100"},
            {"industry": "Business Supplies & Equipment", "external_id": "5567e0fa73696410e4c51200"},
            {"industry": "Capital Markets", "external_id": "5567cdb773696439a9080000"},
            {"industry": "Chemicals", "external_id": "5567e21e73696426a1030000"},
            {"industry": "Civic & Social Organization", "external_id": "5567cdda7369644eed130000"},
            {"industry": "Civil Engineering", "external_id": "5567e13a73696418756e0200"},
            {"industry": "Commercial Real Estate", "external_id": "5567e1887369641d68d40100"},
            {"industry": "Computer & Network Security", "external_id": "5567cd877369644cf94b0000"},
            {"industry": "Computer Games", "external_id": "5567cd8b736964540d0f0000"},
            {"industry": "Computer Hardware", "external_id": "5567e0d47369641233eb0600"},
            {"industry": "Computer Networking", "external_id": "5567cdbe7369643b78360000"},
            {"industry": "Computer Software", "external_id": "5567cd4e7369643b70010000"},
            {"industry": "Construction", "external_id": "5567cd4773696439dd350000"},
            {"industry": "Consumer Electronics", "external_id": "567e1947369641ead570000"},
            {"industry": "Consumer Goods", "external_id": "5567ce987369643b789e0000"},
            {"industry": "Consumer Services", "external_id": "5567d1127261697f2b1d0000"},
            {"industry": "Cosmetics", "external_id": "5567e1ae73696423dc040000"},
            {"industry": "Dairy", "external_id": "5567e8a27369646ddb0b0000"},
            {"industry": "Defense & Space", "external_id": "5567e1097369641b5f810500"},
            {"industry": "Design", "external_id": "5567cdbc73696439d90b0000"},
            {"industry": "E-Learning", "external_id": "5567e19c7369641c48e70100"},
            {"industry": "Education Management", "external_id": "5567ce9e736964540d540000"},
            {"industry": "Electrical/Electronic Manufacturing", "external_id": "5567cd4c73696439c9030000"},
            {"industry": "Entertainment", "external_id": "5567cdd37369643b80510000"},
            {"industry": "Environmental Services", "external_id": "5567ce5b736964540d280000"},
            {"industry": "Events Services", "external_id": "5567cd8e7369645409450000"},
            {"industry": "Executive Office", "external_id": "5567e09473696410dbf00700"},
            {"industry": "Facilities Services", "external_id": "5567ce9c7369643bc9980000"},
            {"industry": "Farming", "external_id": "5567cd4f7369644d2d010000"},
            {"industry": "Financial Services", "external_id": "5567cdd67369643e64020000"},
            {"industry": "Fine Art", "external_id": "5567e2097369642420150000"},
            {"industry": "Fishery", "external_id": "5567f96c7369642a22080000"},
            {"industry": "Food & Beverages", "external_id": "5567ce1e7369643b806a0000"},
            {"industry": "Food Production", "external_id": "5567e1b3736964208b280000"},
            {"industry": "Fund-Raising", "external_id": "5567d2ad7261697f2b1f0100"},
            {"industry": "Furniture", "external_id": "5567cede73696440d0040000"},
            {"industry": "Gambling & Casinos", "external_id": "5567e0cf7369641233e50600"},
            {"industry": "Glass, Ceramics & Concrete", "external_id": "5567cd4f736964397e030000"},
            {"industry": "Government Administration", "external_id": "5567cd527369643981050000"},
            {"industry": "Government Relations", "external_id": "5567e29b736964256c370100"},
            {"industry": "Graphic Design", "external_id": "5567cd4d73696439d9040000"},
            {"industry": "Health, Wellness & Fitness", "external_id": "5567cddb7369644d250c0000"},
            {"industry": "Higher Education", "external_id": "5567cd4c73696453e1300000"},
            {"industry": "Hospital & Health Care", "external_id": "5567cdde73696439812c0000"},
            {"industry": "Hospitality", "external_id": "5567ce9d7369643bc19c0000"},
            {"industry": "Human Resources", "external_id": "5567e0e37369640e5ac10c00"},
            {"industry": "Import & Export", "external_id": "5567ce9d7369645430c50000"},
            {"industry": "Individual & Family Services", "external_id": "5567d02b7369645d8b140000"},
            {"industry": "Industrial Automation", "external_id": "5567e1337369641ad2970000"},
            {"industry": "Information Services", "external_id": "5567e0c97369640d2b3b1600"},
            {"industry": "Information Technology & Services", "external_id": "5567cd4773696439b10b0000"},
            {"industry": "Insurance", "external_id": "5567cdd973696453d93f0000"},
            {"industry": "International Affairs", "external_id": "5567e3657369642f4ec90000"},
            {"industry": "International Trade & Development", "external_id": "5567ce9c7369644eed680000"},
            {"industry": "Internet", "external_id": "5567cd4d736964397e020000"},
            {"industry": "Investment Banking", "external_id": "5567e1ab7369641f6d660100"},
            {"industry": "Investment Management", "external_id": "5567e0bc7369641d11550200"},
            {"industry": "Judiciary", "external_id": "55680a8273696407b61f0000"},
            {"industry": "Law Enforcement", "external_id": "5567e0e073696408da441e00"},
            {"industry": "Law Practice", "external_id": "5567ce1f7369644d391c0000"},
            {"industry": "Legal Services", "external_id": "5567ce2d7369644d25250000"},
            {"industry": "Legislative Office", "external_id": "5567e1797369641c48c10100"},
            {"industry": "Leisure, Travel & Tourism", "external_id": "5567cdd87369643bc12f0000"},
            {"industry": "Libraries", "external_id": "556808697369647bfd420000"},
            {"industry": "Logistics & Supply Chain", "external_id": "5567cd4973696439b9010000"},
            {"industry": "Luxury Goods & Jewelry", "external_id": "5567cda97369644cfd3e0000"},
            {"industry": "Machinery", "external_id": "5567cd4973696439d53c0000"},
            {"industry": "Management Consulting", "external_id": "5567cdd47369643dbf260000"},
            {"industry": "Maritime", "external_id": "5567cd8273696439b1240000"},
            {"industry": "Market Research", "external_id": "5567e1387369641ec75d0200"},
            {"industry": "Marketing & Advertising", "external_id": "5567cd467369644d39040000"},
            {"industry": "Mechanical or Industrial Engineering", "external_id": "5567ce2673696453d95c0000"},
            {"industry": "Media Production", "external_id": "5567e0ea7369640d2ba31600"},
            {"industry": "Medical Devices", "external_id": "5567e1b97369641ea9690200"},
            {"industry": "Medical Practice", "external_id": "5567d0467369645dbc200000"},
            {"industry": "Mental Health Care", "external_id": "5567ce2773696454308f0000"},
            {"industry": "Military", "external_id": "5567e2c572616932bb3b0000"},
            {"industry": "Mining & Metals", "external_id": "5567e3f3736964395d7a0000"},
            {"industry": "Motion Pictures & Film", "external_id": "5567cdd7736964540d130000"},
            {"industry": "Museums & Institutions", "external_id": "5567e15373696422aa0a0000"},
            {"industry": "Music", "external_id": "5567cd4f736964540d050000"},
            {"industry": "Nanotechnology", "external_id": "5567e7be736964110e210000"},
            {"industry": "Newspapers", "external_id": "5567cd4a73696439a9010000"},
            {"industry": "Nonprofit Organization Management", "external_id": "5567cd4773696454303a0000"},
            {"industry": "Oil & Energy", "external_id": "5567cdd97369645624020000"},
            {"industry": "Online Media", "external_id": "5567cdb373696439dd540000"},
            {"industry": "Outsourcing/Offshoring", "external_id": "5567d04173696457ee520000"},
            {"industry": "Package/Freight Delivery", "external_id": "5567e8bb7369641a658f0000"},
            {"industry": "Packaging & Containers", "external_id": "5567e36973696431a4480000"},
            {"industry": "Paper & Forest Products", "external_id": "5567e97f7369641e57730100"},
            {"industry": "Performing Arts", "external_id": "5567e0af7369641ec7300000"},
            {"industry": "Pharmaceuticals", "external_id": "5567e0eb73696410e4bd1200"},
            {"industry": "Philanthropy", "external_id": "5567ce9673696453d99f0000"},
            {"industry": "Photography", "external_id": "5567cd4f7369644cfd250000"},
            {"industry": "Plastics", "external_id": "5567cdda7369644cf95d0000"},
            {"industry": "Political Organization", "external_id": "5567e25f736964256cff0000"},
            {"industry": "Primary/Secondary Education", "external_id": "5567cdd97369645430680000"},
            {"industry": "Printing", "external_id": "5567cd4d7369644d513e0000"},
            {"industry": "Professional Training & Coaching", "external_id": "5567cd49736964541d010000"},
            {"industry": "Program Development", "external_id": "5567e2907369642433e60200"},
            {"industry": "Public Policy", "external_id": "5567e28a7369642ae2500000"},
            {"industry": "Public Relations & Communications", "external_id": "5567ce5973696453d9780000"},
            {"industry": "Public Safety", "external_id": "5567cd4a7369643ba9010000"},
            {"industry": "Publishing", "external_id": "5567ce5b73696439a17a0000"},
            {"industry": "Railroad Manufacture", "external_id": "5567e14673696416d38c0300"},
            {"industry": "Ranching", "external_id": "5567fd5a73696442b0f20000"},
            {"industry": "Real Estate", "external_id": "5567cd477369645401010000"},
            {"industry": "Recreational Facilities & Services", "external_id": "5567e134736964214f5e0000"},
            {"industry": "Religious Institutions", "external_id": "5567e0f27369640e5aed0c00"},
            {"industry": "Renewables & Environment", "external_id": "5567cd49736964540d020000"},
            {"industry": "Research", "external_id": "5567e09f736964160ebb0100"},
            {"industry": "Restaurants", "external_id": "5567e0e0736964198de70700"},
            {"industry": "Retail", "external_id": "5567ced173696450cb580000"},
            {"industry": "Security & Investigations", "external_id": "5567e19b7369641ead740000"},
            {"industry": "Semiconductors", "external_id": "5567e0d87369640e5aa30c00"},
            {"industry": "Shipbuilding", "external_id": "5568047d7369646d406c0000"},
            {"industry": "Sporting Goods", "external_id": "5567e113736964198d5e0800"},
            {"industry": "Sports", "external_id": "5567ce227369644eed290000"},
            {"industry": "Staffing & Recruiting", "external_id": "5567e09973696410db020800"},
            {"industry": "Supermarkets", "external_id": "5567e2a97369642a553d0000"},
            {"industry": "Telecommunications", "external_id": "5567cd4c7369644d39080000"},
            {"industry": "Textiles", "external_id": "5567e1327369641d91ce0300"},
            {"industry": "Think Tanks", "external_id": "5567e1de7369642069ea0100"},
            {"industry": "Tobacco", "external_id": "55680085736964551e070000"},
            {"industry": "Translation & Localization", "external_id": "5567e1097369641d91230300"},
            {"industry": "Transportation/Trucking/Railroad", "external_id": "5567cd4e7369644cf93b0000"},
            {"industry": "Utilities", "external_id": "5567e2127369642420170000"},
            {"industry": "Venture Capital & Private Equity", "external_id": "5567e1587369641c48370000"},
            {"industry": "Veterinary", "external_id": "5567ce9673696439d5c10000"},
            {"industry": "Warehousing", "external_id": "5567e127736964181e700200"},
            {"industry": "Wholesale", "external_id": "5567d01e73696457ee100000"},
            {"industry": "Wine & Spirits", "external_id": "5567cd4d7369643b78100000"},
            {"industry": "Wireless", "external_id": "5567e3ca736964371b130000"},
            {"industry": "Writing & Editing", "external_id": "5567cdd973696439a1370000"}
        ]
        
        # Check existing tags
        existing_tags = await db_service.get_industry_tags()
        existing_industries = {tag['industry'].lower() for tag in existing_tags}
        
        print(f"Found {len(existing_tags)} existing industry tags")
        
        # Filter out existing tags and prepare new ones
        new_tags = []
        for industry_data in comprehensive_industries:
            if industry_data['industry'].lower() not in existing_industries:
                tag_data = {
                    "id": generate_id(),
                    "industry": industry_data['industry'],
                    "external_id": industry_data['external_id'],
                    "description": f"{industry_data['industry']} industry classification",
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                new_tags.append(tag_data)
        
        print(f"Adding {len(new_tags)} new industry tags")
        
        if new_tags:
            await db_service.bulk_insert_industry_tags(new_tags)
            print("✅ Successfully added industry tags:")
            for tag in new_tags:
                print(f"  • {tag['industry']} -> {tag['external_id']}")
        else:
            print("✅ All industry tags already exist")
        
        # Display final count
        all_tags = await db_service.get_industry_tags()
        print(f"\n📊 Total industry tags in database: {len(all_tags)}")
        
        # Create industry lookup data for AI Agent
        industry_lookup = {}
        for tag in all_tags:
            industry_lookup[tag['industry'].lower()] = {
                "id": tag['id'],
                "external_id": tag['external_id'],
                "industry": tag['industry'],
                "description": tag.get('description', ''),
                "url": f"/api/industries/{tag['external_id']}"
            }
        
        print(f"\n🤖 AI Agent can now access {len(industry_lookup)} industries")
        print("Sample industry URLs:")
        for i, (key, value) in enumerate(list(industry_lookup.items())[:5]):
            print(f"  • {value['industry']}: {value['url']}")
        
        return industry_lookup
        
    except Exception as e:
        print(f"❌ Error populating industries: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        await db_service.disconnect()

if __name__ == "__main__":
    print("🚀 Populating comprehensive industry data for AI Agent...")
    result = asyncio.run(populate_comprehensive_industries())
    if result:
        print("✅ Industry data population complete!")
        print(f"AI Agent now has access to {len(result)} industries with URLs")
    else:
        print("❌ Failed to populate industry data")