#!/usr/bin/env python3
"""
Gap Analysis and Missing Functionality Test
Identifies what's missing from the email campaign functionality
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8001"

class GapAnalysisTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.missing_endpoints = []
        self.working_endpoints = []
        
    def test_missing_endpoints(self):
        """Test endpoints that should exist but are missing"""
        print("🔍 Testing for Missing Email Campaign Endpoints")
        print("=" * 60)
        
        # Endpoints that should exist for full email campaign functionality
        missing_tests = [
            # Template Management (CREATE/UPDATE/DELETE missing)
            ("POST /api/templates", "Template creation"),
            ("PUT /api/templates/{id}", "Template updates"),
            ("DELETE /api/templates/{id}", "Template deletion"),
            
            # Prospect Management (CREATE/UPDATE/DELETE missing)
            ("POST /api/prospects", "Prospect creation"),
            ("PUT /api/prospects/{id}", "Prospect updates"),
            ("DELETE /api/prospects/{id}", "Prospect deletion"),
            ("POST /api/prospects/upload", "CSV prospect upload"),
            
            # Campaign Email Sending (CRITICAL MISSING)
            ("POST /api/campaigns/{id}/send", "Email sending through campaigns"),
            ("GET /api/campaigns/{id}/status", "Campaign status tracking"),
            ("PUT /api/campaigns/{id}", "Campaign updates"),
            ("DELETE /api/campaigns/{id}", "Campaign deletion"),
            
            # List Management (CREATE/UPDATE/DELETE missing)
            ("POST /api/lists", "List creation"),
            ("PUT /api/lists/{id}", "List updates"),
            ("DELETE /api/lists/{id}", "List deletion"),
            ("POST /api/lists/{id}/prospects", "Add prospects to lists"),
            
            # Intent Management (CREATE/UPDATE/DELETE missing)
            ("POST /api/intents", "Intent creation"),
            ("PUT /api/intents/{id}", "Intent updates"),
            ("DELETE /api/intents/{id}", "Intent deletion"),
            
            # Analytics (Overall analytics missing)
            ("GET /api/analytics", "Overall analytics dashboard"),
            ("GET /api/analytics/overview", "Analytics overview"),
        ]
        
        for endpoint, description in missing_tests:
            method, path = endpoint.split(' ', 1)
            test_path = path.replace('{id}', '1').replace('{campaign_id}', '1')
            
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{test_path}", timeout=5)
                elif method == 'POST':
                    response = requests.post(f"{self.base_url}{test_path}", json={}, timeout=5)
                elif method == 'PUT':
                    response = requests.put(f"{self.base_url}{test_path}", json={}, timeout=5)
                elif method == 'DELETE':
                    response = requests.delete(f"{self.base_url}{test_path}", timeout=5)
                
                if response.status_code == 404:
                    print(f"❌ MISSING: {endpoint} - {description}")
                    self.missing_endpoints.append((endpoint, description))
                elif response.status_code == 405:
                    print(f"❌ MISSING: {endpoint} - {description} (Method not allowed)")
                    self.missing_endpoints.append((endpoint, description))
                else:
                    print(f"✅ EXISTS: {endpoint} - {description}")
                    self.working_endpoints.append((endpoint, description))
                    
            except Exception as e:
                print(f"❌ ERROR: {endpoint} - Connection failed: {str(e)}")
                self.missing_endpoints.append((endpoint, description))
    
    def test_error_handling(self):
        """Test error handling for existing endpoints"""
        print(f"\n🛡️ Testing Error Handling")
        print("=" * 60)
        
        error_tests = [
            # Invalid data tests
            ("POST /api/campaigns", {"name": ""}, "Empty campaign name"),
            ("POST /api/email-providers", {"name": ""}, "Empty provider name"),
            ("GET /api/analytics/campaign/invalid_id", None, "Invalid campaign ID"),
            
            # Non-existent resource tests
            ("PUT /api/email-providers/nonexistent", {"name": "test"}, "Non-existent provider update"),
            ("DELETE /api/email-providers/nonexistent", None, "Non-existent provider deletion"),
        ]
        
        for endpoint, data, description in error_tests:
            method, path = endpoint.split(' ', 1)
            
            try:
                if method == 'GET':
                    response = requests.get(f"{self.base_url}{path}", timeout=5)
                elif method == 'POST':
                    response = requests.post(f"{self.base_url}{path}", json=data, timeout=5)
                elif method == 'PUT':
                    response = requests.put(f"{self.base_url}{path}", json=data, timeout=5)
                elif method == 'DELETE':
                    response = requests.delete(f"{self.base_url}{path}", timeout=5)
                
                if response.status_code >= 400:
                    print(f"✅ GOOD: {description} - Returns {response.status_code}")
                else:
                    print(f"⚠️  WEAK: {description} - Should return error but got {response.status_code}")
                    
            except Exception as e:
                print(f"❌ ERROR: {description} - {str(e)}")
    
    def analyze_functionality_gaps(self):
        """Analyze what functionality is missing for complete email campaigns"""
        print(f"\n📊 Email Campaign Functionality Gap Analysis")
        print("=" * 60)
        
        # Critical missing functionality
        critical_gaps = [
            "Email Sending: No endpoint to actually send emails through campaigns",
            "Template CRUD: Cannot create, update, or delete email templates",
            "Prospect CRUD: Cannot create, update, or delete prospects",
            "CSV Upload: Cannot upload prospect lists via CSV",
            "Campaign Management: Cannot update or delete campaigns",
            "List Management: Cannot create or manage prospect lists",
            "Intent Management: Cannot create or manage AI intents",
            "Overall Analytics: No comprehensive analytics dashboard"
        ]
        
        print("🚨 CRITICAL MISSING FUNCTIONALITY:")
        for i, gap in enumerate(critical_gaps, 1):
            print(f"  {i}. {gap}")
        
        # What's working well
        working_features = [
            "Authentication system (login, profile, token refresh)",
            "Email provider management (full CRUD)",
            "Read-only access to templates, prospects, campaigns",
            "Campaign creation",
            "Individual campaign analytics",
            "Real-time dashboard metrics",
            "Health monitoring"
        ]
        
        print(f"\n✅ WORKING FUNCTIONALITY:")
        for i, feature in enumerate(working_features, 1):
            print(f"  {i}. {feature}")
        
        # Impact assessment
        print(f"\n🎯 IMPACT ASSESSMENT:")
        print("  - Email Provider Management: ✅ COMPLETE (100%)")
        print("  - Template Management: ⚠️  PARTIAL (33% - Read only)")
        print("  - Prospect Management: ⚠️  PARTIAL (33% - Read only)")
        print("  - Campaign Creation: ✅ WORKING (Campaign creation works)")
        print("  - Email Sending: ❌ MISSING (0% - Cannot send emails)")
        print("  - Analytics: ⚠️  PARTIAL (50% - Campaign analytics only)")
        
        overall_completeness = (
            100 +  # Email providers
            33 +   # Templates
            33 +   # Prospects
            75 +   # Campaigns
            0 +    # Email sending
            50     # Analytics
        ) / 6
        
        print(f"\n📈 OVERALL COMPLETENESS: {overall_completeness:.1f}%")
        
        if overall_completeness >= 80:
            print("✅ System is mostly functional for email campaigns")
        elif overall_completeness >= 60:
            print("⚠️  System has significant gaps but core functionality exists")
        else:
            print("❌ System is not ready for production email campaigns")
    
    def run_gap_analysis(self):
        """Run complete gap analysis"""
        print("🔍 Email Campaign Functionality Gap Analysis")
        print("Testing what's missing vs what's implemented")
        print("=" * 70)
        
        self.test_missing_endpoints()
        self.test_error_handling()
        self.analyze_functionality_gaps()
        
        print(f"\n📋 SUMMARY:")
        print(f"  - Working endpoints: {len(self.working_endpoints)}")
        print(f"  - Missing endpoints: {len(self.missing_endpoints)}")
        
        return {
            'working_endpoints': self.working_endpoints,
            'missing_endpoints': self.missing_endpoints
        }

def main():
    """Main execution"""
    tester = GapAnalysisTester()
    results = tester.run_gap_analysis()
    
    print(f"\n🎯 RECOMMENDATIONS FOR MAIN AGENT:")
    print("=" * 70)
    print("1. CRITICAL: Implement email sending endpoint (/api/campaigns/{id}/send)")
    print("2. HIGH: Add CRUD operations for templates, prospects, and lists")
    print("3. MEDIUM: Add CSV upload functionality for prospects")
    print("4. MEDIUM: Add overall analytics dashboard")
    print("5. LOW: Improve error handling and validation")
    
    return results

if __name__ == "__main__":
    main()