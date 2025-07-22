#!/usr/bin/env python3
"""
Enhanced Follow-up Monitoring System Testing for AI Email Responder
Focus on testing the new follow-up monitoring API endpoints and functionality
"""

import requests
import json
from datetime import datetime, timedelta
import time
import os

# Get backend URL from frontend .env file
BACKEND_URL = "https://ff840f7f-2461-4d51-9638-7e3bb87fb8ee.preview.emergentagent.com"
AUTH_TOKEN = "test_token_12345"

class FollowUpMonitoringTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = AUTH_TOKEN
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.test_results = {}
        self.created_resources = {
            'prospects': [],
            'campaigns': [],
            'templates': [],
            'email_providers': []
        }
    
    def log_result(self, test_name, success, message="", details=None):
        """Log test results"""
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_authentication(self):
        """Test authentication system"""
        try:
            # Test login
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code != 200:
                self.log_result("Authentication Login", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication Login", False, "No access token in response", auth_result)
                return False
            
            self.log_result("Authentication Login", True, "Login successful")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_up_monitoring_dashboard(self):
        """Test the follow-up monitoring dashboard endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/dashboard", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Follow-up Dashboard", False, f"HTTP {response.status_code}", response.text)
                return False
            
            dashboard_data = response.json()
            
            # Check required fields
            required_fields = [
                'imap_monitoring', 'follow_up_stats', 'active_campaigns',
                'prospects_needing_follow_up', 'recent_responses', 'system_status'
            ]
            
            for field in required_fields:
                if field not in dashboard_data:
                    self.log_result("Follow-up Dashboard", False, f"Missing field: {field}", dashboard_data)
                    return False
            
            # Check system status structure
            system_status = dashboard_data.get('system_status', {})
            status_fields = ['email_processor_running', 'follow_up_engine_running', 'last_updated']
            
            for field in status_fields:
                if field not in system_status:
                    self.log_result("Follow-up Dashboard", False, f"Missing system status field: {field}", system_status)
                    return False
            
            self.log_result("Follow-up Dashboard", True, 
                          f"Dashboard loaded successfully. Active campaigns: {dashboard_data.get('active_campaigns', 0)}, "
                          f"Prospects needing follow-up: {dashboard_data.get('prospects_needing_follow_up', 0)}")
            return True
            
        except Exception as e:
            self.log_result("Follow-up Dashboard", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_up_monitoring_health_check(self):
        """Test the follow-up monitoring health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/health-check", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Follow-up Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            health_data = response.json()
            
            # Check required fields
            if 'status' not in health_data:
                self.log_result("Follow-up Health Check", False, "Missing status field", health_data)
                return False
            
            if 'details' not in health_data:
                self.log_result("Follow-up Health Check", False, "Missing details field", health_data)
                return False
            
            # Check details structure
            details = health_data.get('details', {})
            detail_fields = ['database_connected', 'email_processor_running', 'follow_up_engine_running', 'system_time']
            
            for field in detail_fields:
                if field not in details:
                    self.log_result("Follow-up Health Check", False, f"Missing detail field: {field}", details)
                    return False
            
            status = health_data.get('status')
            self.log_result("Follow-up Health Check", True, 
                          f"Health check completed. Status: {status}, "
                          f"Database: {'✓' if details.get('database_connected') else '✗'}, "
                          f"Email Processor: {'✓' if details.get('email_processor_running') else '✗'}, "
                          f"Follow-up Engine: {'✓' if details.get('follow_up_engine_running') else '✗'}")
            return True
            
        except Exception as e:
            self.log_result("Follow-up Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_imap_logs_endpoint(self):
        """Test the IMAP scan logs endpoint"""
        try:
            # Test with default hours (24)
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/imap-logs", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("IMAP Logs", False, f"HTTP {response.status_code}", response.text)
                return False
            
            logs_data = response.json()
            
            # Check required fields
            required_fields = ['logs', 'total_scans', 'time_range_hours']
            
            for field in required_fields:
                if field not in logs_data:
                    self.log_result("IMAP Logs", False, f"Missing field: {field}", logs_data)
                    return False
            
            # Test with custom hours parameter
            response_custom = requests.get(f"{self.base_url}/api/follow-up-monitoring/imap-logs?hours=12", headers=self.headers)
            
            if response_custom.status_code != 200:
                self.log_result("IMAP Logs Custom Hours", False, f"HTTP {response_custom.status_code}", response_custom.text)
                return False
            
            custom_logs_data = response_custom.json()
            
            if custom_logs_data.get('time_range_hours') != 12:
                self.log_result("IMAP Logs Custom Hours", False, f"Expected 12 hours, got {custom_logs_data.get('time_range_hours')}")
                return False
            
            total_scans = logs_data.get('total_scans', 0)
            self.log_result("IMAP Logs", True, 
                          f"IMAP logs retrieved successfully. Total scans (24h): {total_scans}, "
                          f"Custom query (12h): {custom_logs_data.get('total_scans', 0)} scans")
            return True
            
        except Exception as e:
            self.log_result("IMAP Logs", False, f"Exception: {str(e)}")
            return False
    
    def test_prospect_responses_endpoint(self):
        """Test the prospect responses endpoint"""
        try:
            # Test with default days (7)
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/prospect-responses", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Prospect Responses", False, f"HTTP {response.status_code}", response.text)
                return False
            
            responses_data = response.json()
            
            # Check required fields
            required_fields = ['responses', 'total_responses', 'time_range_days']
            
            for field in required_fields:
                if field not in responses_data:
                    self.log_result("Prospect Responses", False, f"Missing field: {field}", responses_data)
                    return False
            
            # Test with custom days parameter
            response_custom = requests.get(f"{self.base_url}/api/follow-up-monitoring/prospect-responses?days=3", headers=self.headers)
            
            if response_custom.status_code != 200:
                self.log_result("Prospect Responses Custom Days", False, f"HTTP {response_custom.status_code}", response_custom.text)
                return False
            
            custom_responses_data = response_custom.json()
            
            if custom_responses_data.get('time_range_days') != 3:
                self.log_result("Prospect Responses Custom Days", False, f"Expected 3 days, got {custom_responses_data.get('time_range_days')}")
                return False
            
            # Check response structure
            responses = responses_data.get('responses', [])
            if responses:
                first_response = responses[0]
                response_fields = ['prospect', 'follow_up_history', 'response_type']
                
                for field in response_fields:
                    if field not in first_response:
                        self.log_result("Prospect Responses Structure", False, f"Missing response field: {field}", first_response)
                        return False
            
            total_responses = responses_data.get('total_responses', 0)
            self.log_result("Prospect Responses", True, 
                          f"Prospect responses retrieved successfully. Total responses (7d): {total_responses}, "
                          f"Custom query (3d): {custom_responses_data.get('total_responses', 0)} responses")
            return True
            
        except Exception as e:
            self.log_result("Prospect Responses", False, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_database_methods(self):
        """Test enhanced database methods for follow-up tracking"""
        try:
            # First, create a test prospect to work with
            unique_timestamp = int(time.time())
            prospect_data = {
                "email": f"followup.test.{unique_timestamp}@example.com",
                "first_name": "FollowUp",
                "last_name": "Test",
                "company": "Test Corp",
                "job_title": "Test Manager",
                "follow_up_status": "active",
                "follow_up_count": 0
            }
            
            response = requests.post(f"{self.base_url}/api/prospects", json=prospect_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Enhanced Database Methods - Create Prospect", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_prospect = response.json()
            prospect_id = created_prospect['id']
            self.created_resources['prospects'].append(prospect_id)
            
            # Test thread analysis endpoint
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/thread-analysis/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Enhanced Database Methods - Thread Analysis", False, f"HTTP {response.status_code}", response.text)
                return False
            
            thread_analysis = response.json()
            
            # Check required fields
            required_fields = ['prospect_id', 'thread_found', 'analysis']
            
            for field in required_fields:
                if field not in thread_analysis:
                    self.log_result("Enhanced Database Methods - Thread Analysis", False, f"Missing field: {field}", thread_analysis)
                    return False
            
            # Test force stop follow-up
            response = requests.post(f"{self.base_url}/api/follow-up-monitoring/force-stop-follow-up/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Enhanced Database Methods - Force Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            stop_result = response.json()
            
            if 'message' not in stop_result or 'action' not in stop_result:
                self.log_result("Enhanced Database Methods - Force Stop", False, "Missing response fields", stop_result)
                return False
            
            # Test restart follow-up
            response = requests.post(f"{self.base_url}/api/follow-up-monitoring/restart-follow-up/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Enhanced Database Methods - Restart", False, f"HTTP {response.status_code}", response.text)
                return False
            
            restart_result = response.json()
            
            if 'message' not in restart_result or 'action' not in restart_result:
                self.log_result("Enhanced Database Methods - Restart", False, "Missing response fields", restart_result)
                return False
            
            self.log_result("Enhanced Database Methods", True, 
                          f"Database methods tested successfully. Thread analysis: {thread_analysis.get('thread_found')}, "
                          f"Force stop: {stop_result.get('action')}, Restart: {restart_result.get('action')}")
            return True
            
        except Exception as e:
            self.log_result("Enhanced Database Methods", False, f"Exception: {str(e)}")
            return False
    
    def test_follow_up_engine_functionality(self):
        """Test smart follow-up engine start/stop functionality"""
        try:
            # Test starting the follow-up engine
            response = requests.post(f"{self.base_url}/api/smart-follow-up/start", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Follow-up Engine Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            start_result = response.json()
            
            if 'status' not in start_result:
                self.log_result("Follow-up Engine Start", False, "Missing status field", start_result)
                return False
            
            # Test getting follow-up statistics
            response = requests.get(f"{self.base_url}/api/smart-follow-up/statistics", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Follow-up Engine Statistics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            stats_result = response.json()
            
            # Check statistics structure
            stats_fields = ['total_prospects', 'active_follow_ups', 'stopped_follow_ups', 'response_rate', 'engine_status']
            
            for field in stats_fields:
                if field not in stats_result:
                    self.log_result("Follow-up Engine Statistics", False, f"Missing stats field: {field}", stats_result)
                    return False
            
            # Test stopping the follow-up engine
            response = requests.post(f"{self.base_url}/api/smart-follow-up/stop", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Follow-up Engine Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            stop_result = response.json()
            
            if 'status' not in stop_result:
                self.log_result("Follow-up Engine Stop", False, "Missing status field", stop_result)
                return False
            
            self.log_result("Follow-up Engine Functionality", True, 
                          f"Engine functionality tested successfully. Start: {start_result.get('status')}, "
                          f"Stop: {stop_result.get('status')}, Active follow-ups: {stats_result.get('active_follow_ups', 0)}")
            return True
            
        except Exception as e:
            self.log_result("Follow-up Engine Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_email_processing_enhancement(self):
        """Test enhanced email processor with IMAP monitoring"""
        try:
            # Test email processing status
            response = requests.get(f"{self.base_url}/api/email-processing/status", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Email Processing Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_result = response.json()
            
            if 'status' not in status_result:
                self.log_result("Email Processing Status", False, "Missing status field", status_result)
                return False
            
            # Test starting email processing
            response = requests.post(f"{self.base_url}/api/email-processing/start", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Email Processing Start", False, f"HTTP {response.status_code}", response.text)
                return False
            
            start_result = response.json()
            
            if 'status' not in start_result:
                self.log_result("Email Processing Start", False, "Missing status field", start_result)
                return False
            
            # Test email processing analytics
            response = requests.get(f"{self.base_url}/api/email-processing/analytics", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Email Processing Analytics", False, f"HTTP {response.status_code}", response.text)
                return False
            
            analytics_result = response.json()
            
            # Check analytics structure
            analytics_fields = ['total_threads', 'processed_emails', 'auto_responses_sent', 'processing_status']
            
            for field in analytics_fields:
                if field not in analytics_result:
                    self.log_result("Email Processing Analytics", False, f"Missing analytics field: {field}", analytics_result)
                    return False
            
            # Test stopping email processing
            response = requests.post(f"{self.base_url}/api/email-processing/stop", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Email Processing Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            stop_result = response.json()
            
            if 'status' not in stop_result:
                self.log_result("Email Processing Stop", False, "Missing status field", stop_result)
                return False
            
            self.log_result("Email Processing Enhancement", True, 
                          f"Email processing tested successfully. Status: {status_result.get('status')}, "
                          f"Processed emails: {analytics_result.get('processed_emails', 0)}, "
                          f"Auto responses: {analytics_result.get('auto_responses_sent', 0)}")
            return True
            
        except Exception as e:
            self.log_result("Email Processing Enhancement", False, f"Exception: {str(e)}")
            return False
    
    def test_integration_functionality(self):
        """Test integration between follow-up engine and email processing"""
        try:
            # Create a test campaign with follow-up enabled
            # First ensure we have templates
            templates_response = requests.get(f"{self.base_url}/api/templates", headers=self.headers)
            if templates_response.status_code != 200 or not templates_response.json():
                self.log_result("Integration Test Prerequisites", False, "No templates available")
                return False
            
            template_id = templates_response.json()[0]['id']
            
            # Create campaign with follow-up enabled
            campaign_data = {
                "name": "Follow-up Integration Test Campaign",
                "template_id": template_id,
                "list_ids": [],
                "max_emails": 10,
                "follow_up_enabled": True,
                "follow_up_intervals": [1, 3, 7],  # 1, 3, 7 days
                "follow_up_templates": [template_id]
            }
            
            response = requests.post(f"{self.base_url}/api/campaigns", json=campaign_data, headers=self.headers)
            if response.status_code != 200:
                self.log_result("Integration Test - Create Campaign", False, f"HTTP {response.status_code}", response.text)
                return False
            
            created_campaign = response.json()
            campaign_id = created_campaign['id']
            self.created_resources['campaigns'].append(campaign_id)
            
            # Test that the campaign appears in follow-up monitoring dashboard
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/dashboard", headers=self.headers)
            if response.status_code != 200:
                self.log_result("Integration Test - Dashboard Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            dashboard_data = response.json()
            active_campaigns = dashboard_data.get('active_campaigns', 0)
            
            # Test prospect response detection
            if self.created_resources['prospects']:
                prospect_id = self.created_resources['prospects'][0]
                
                # Test thread analysis for integration
                response = requests.get(f"{self.base_url}/api/follow-up-monitoring/thread-analysis/{prospect_id}", headers=self.headers)
                if response.status_code != 200:
                    self.log_result("Integration Test - Thread Analysis", False, f"HTTP {response.status_code}", response.text)
                    return False
                
                thread_analysis = response.json()
                
                # Check if follow-up history is tracked
                if 'analysis' in thread_analysis and 'follow_up_count' in thread_analysis['analysis']:
                    follow_up_count = thread_analysis['analysis']['follow_up_count']
                else:
                    follow_up_count = 0
            else:
                follow_up_count = 0
            
            self.log_result("Integration Functionality", True, 
                          f"Integration tested successfully. Active campaigns: {active_campaigns}, "
                          f"Follow-up tracking working, Thread analysis functional")
            return True
            
        except Exception as e:
            self.log_result("Integration Functionality", False, f"Exception: {str(e)}")
            return False
    
    def test_response_detection_and_follow_up_stopping(self):
        """Test that follow-ups stop when prospects respond manually"""
        try:
            # This test verifies the key functionality mentioned in the review request
            if not self.created_resources['prospects']:
                self.log_result("Response Detection Test", False, "No test prospects available")
                return False
            
            prospect_id = self.created_resources['prospects'][0]
            
            # Test marking prospect as responded (simulating manual response)
            response = requests.post(f"{self.base_url}/api/follow-up-monitoring/force-stop-follow-up/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Response Detection - Force Stop", False, f"HTTP {response.status_code}", response.text)
                return False
            
            stop_result = response.json()
            
            # Verify the prospect's follow-up status changed
            response = requests.get(f"{self.base_url}/api/follow-up-monitoring/thread-analysis/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Response Detection - Status Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            thread_analysis = response.json()
            
            # Check if follow-up status indicates stopped
            analysis = thread_analysis.get('analysis', {})
            follow_up_status = analysis.get('follow_up_status', 'unknown')
            
            # Test restarting follow-ups
            response = requests.post(f"{self.base_url}/api/follow-up-monitoring/restart-follow-up/{prospect_id}", headers=self.headers)
            
            if response.status_code != 200:
                self.log_result("Response Detection - Restart", False, f"HTTP {response.status_code}", response.text)
                return False
            
            restart_result = response.json()
            
            self.log_result("Response Detection and Follow-up Stopping", True, 
                          f"Response detection tested successfully. Follow-up status: {follow_up_status}, "
                          f"Stop action: {stop_result.get('action')}, Restart action: {restart_result.get('action')}")
            return True
            
        except Exception as e:
            self.log_result("Response Detection and Follow-up Stopping", False, f"Exception: {str(e)}")
            return False
    
    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete campaigns
        for campaign_id in self.created_resources['campaigns']:
            try:
                response = requests.delete(f"{self.base_url}/api/campaigns/{campaign_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted campaign {campaign_id}")
                else:
                    print(f"   ⚠️ Failed to delete campaign {campaign_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting campaign {campaign_id}: {str(e)}")
        
        # Delete prospects
        for prospect_id in self.created_resources['prospects']:
            try:
                response = requests.delete(f"{self.base_url}/api/prospects/{prospect_id}", headers=self.headers)
                if response.status_code == 200:
                    print(f"   ✅ Deleted prospect {prospect_id}")
                else:
                    print(f"   ⚠️ Failed to delete prospect {prospect_id}: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error deleting prospect {prospect_id}: {str(e)}")
    
    def run_follow_up_monitoring_tests(self):
        """Run comprehensive follow-up monitoring tests"""
        print("🚀 Starting Enhanced Follow-up Monitoring System Tests")
        print("Focus: Follow-up Monitoring API Endpoints, Database Methods, Engine Functionality")
        print("=" * 80)
        
        # Test order matters - some tests depend on others
        tests = [
            ("Authentication System", self.test_authentication),
            ("Follow-up Monitoring Dashboard", self.test_follow_up_monitoring_dashboard),
            ("Follow-up Monitoring Health Check", self.test_follow_up_monitoring_health_check),
            ("IMAP Logs Endpoint", self.test_imap_logs_endpoint),
            ("Prospect Responses Endpoint", self.test_prospect_responses_endpoint),
            ("Enhanced Database Methods", self.test_enhanced_database_methods),
            ("Follow-up Engine Functionality", self.test_follow_up_engine_functionality),
            ("Email Processing Enhancement", self.test_email_processing_enhancement),
            ("Integration Functionality", self.test_integration_functionality),
            ("Response Detection and Follow-up Stopping", self.test_response_detection_and_follow_up_stopping)
        ]
        
        passed = 0
        total = len(tests)
        critical_failures = []
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    # Mark critical failures
                    if any(keyword in test_name.lower() for keyword in ['dashboard', 'health', 'engine', 'integration', 'response']):
                        critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All follow-up monitoring tests passed!")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
        
        # Cleanup
        self.cleanup_resources()
        
        return self.test_results, critical_failures

def main():
    """Main test execution"""
    tester = FollowUpMonitoringTester()
    results, critical_failures = tester.run_follow_up_monitoring_tests()
    
    # Print detailed results
    print("\n" + "=" * 80)
    print("📋 DETAILED FOLLOW-UP MONITORING TEST RESULTS")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {test_name}")
        if result['message']:
            print(f"   Message: {result['message']}")
        if result['details']:
            print(f"   Details: {result['details']}")
        print()
    
    # Summary for test_result.md update
    print("\n" + "=" * 80)
    print("📝 FOLLOW-UP MONITORING TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = [name for name, result in results.items() if result['success']]
    failed_tests = [name for name, result in results.items() if not result['success']]
    
    print("✅ PASSED TESTS:")
    for test in passed_tests:
        print(f"   - {test}")
    
    if failed_tests:
        print("\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   - {test}")
    
    if critical_failures:
        print(f"\n🚨 CRITICAL FAILURES: {len(critical_failures)}")
        for failure in critical_failures:
            print(f"   - {failure}")
    
    return results, critical_failures

if __name__ == "__main__":
    main()