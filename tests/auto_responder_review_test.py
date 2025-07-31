#!/usr/bin/env python3
"""
Auto-Responder System Review Testing - January 2025
Testing the specific functionality requested in the review:

1. Email Provider Configuration (particularly Gmail)
2. Auto Responder Services Status
3. IMAP Configuration
4. Intent Management
5. Template System
6. Database Connection
7. Groq AI Integration

Focus on the auto-responder functionality and email provider configuration.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://6b79b9a6-93ed-4a33-b1a5-f766f54ddce0.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class AutoResponderReviewTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = {}
        
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate(self):
        """Authenticate and get access token"""
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "username": USERNAME,
                "password": PASSWORD
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                self.log_result("Authentication", True, "Login successful")
                return True
            else:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_email_provider_configuration(self):
        """Test Email Provider Configuration - particularly Gmail"""
        print("\n🧪 Testing Email Provider Configuration")
        
        try:
            # Get existing email providers
            response = self.session.get(f"{BASE_URL}/email-providers")
            
            if response.status_code != 200:
                self.log_result("Email Providers GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            self.log_result("Email Providers GET", True, f"Found {len(providers)} email providers")
            
            # Check for Gmail providers
            gmail_providers = [p for p in providers if 'gmail' in p.get('provider_type', '').lower() or 'gmail' in p.get('name', '').lower()]
            
            if gmail_providers:
                self.log_result("Gmail Provider Check", True, f"Found {len(gmail_providers)} Gmail providers")
                
                # Check first Gmail provider configuration
                gmail_provider = gmail_providers[0]
                required_fields = ['id', 'name', 'email_address', 'smtp_host', 'smtp_port', 'imap_host', 'imap_port']
                missing_fields = [field for field in required_fields if not gmail_provider.get(field)]
                
                if missing_fields:
                    self.log_result("Gmail Provider Configuration", False, f"Missing fields: {missing_fields}", gmail_provider)
                    return False
                else:
                    self.log_result("Gmail Provider Configuration", True, f"Gmail provider properly configured: {gmail_provider['name']}")
            else:
                self.log_result("Gmail Provider Check", False, "No Gmail providers found")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Email Provider Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_responder_services_status(self):
        """Test Auto Responder Services Status"""
        print("\n🧪 Testing Auto Responder Services Status")
        
        try:
            # Get services status
            response = self.session.get(f"{BASE_URL}/services/status")
            
            if response.status_code != 200:
                self.log_result("Services Status GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            status_data = response.json()
            self.log_result("Services Status GET", True, "Services status retrieved")
            
            # Check for required services
            services = status_data.get('services', {})
            required_services = ['smart_follow_up_engine', 'email_processor']
            
            for service_name in required_services:
                if service_name not in services:
                    self.log_result(f"{service_name} Status", False, f"Service {service_name} not found in status")
                    return False
                
                service_status = services[service_name].get('status', 'unknown')
                self.log_result(f"{service_name} Status", True, f"Status: {service_status}")
            
            # Check overall status
            overall_status = status_data.get('overall_status', 'unknown')
            if overall_status in ['healthy', 'running']:
                self.log_result("Overall Services Status", True, f"Overall status: {overall_status}")
            else:
                self.log_result("Overall Services Status", False, f"Overall status: {overall_status}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Auto Responder Services Status", False, f"Exception: {str(e)}")
            return False
    
    def test_imap_configuration(self):
        """Test IMAP Configuration"""
        print("\n🧪 Testing IMAP Configuration")
        
        try:
            # First get email providers
            response = self.session.get(f"{BASE_URL}/email-providers")
            
            if response.status_code != 200:
                self.log_result("Get Providers for IMAP", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            
            if not providers:
                self.log_result("IMAP Configuration", False, "No providers available to test IMAP")
                return False
            
            # Test IMAP status for first provider
            provider_id = providers[0]['id']
            provider_name = providers[0]['name']
            
            response = self.session.get(f"{BASE_URL}/email-providers/{provider_id}/imap-status")
            
            if response.status_code != 200:
                self.log_result("IMAP Status Check", False, f"HTTP {response.status_code}", response.text)
                return False
            
            imap_status = response.json()
            self.log_result("IMAP Status Check", True, f"IMAP status retrieved for {provider_name}")
            
            # Check IMAP configuration fields
            required_fields = ['provider_id', 'provider_name', 'imap_enabled', 'is_monitoring', 'email_processor_running']
            missing_fields = [field for field in required_fields if field not in imap_status]
            
            if missing_fields:
                self.log_result("IMAP Configuration Fields", False, f"Missing fields: {missing_fields}", imap_status)
                return False
            else:
                self.log_result("IMAP Configuration Fields", True, "All required IMAP fields present")
            
            # Check if IMAP is enabled
            imap_enabled = imap_status.get('imap_enabled', False)
            is_monitoring = imap_status.get('is_monitoring', False)
            
            self.log_result("IMAP Enabled Status", imap_enabled, f"IMAP enabled: {imap_enabled}")
            self.log_result("IMAP Monitoring Status", is_monitoring, f"IMAP monitoring: {is_monitoring}")
            
            return True
            
        except Exception as e:
            self.log_result("IMAP Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_intent_management(self):
        """Test Intent Management"""
        print("\n🧪 Testing Intent Management")
        
        try:
            # Get intents
            response = self.session.get(f"{BASE_URL}/intents")
            
            if response.status_code != 200:
                self.log_result("Intents GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intents = response.json()
            self.log_result("Intents GET", True, f"Found {len(intents)} intents")
            
            # Check for auto-response intents
            auto_response_intents = [intent for intent in intents if intent.get('auto_respond', False)]
            
            if auto_response_intents:
                self.log_result("Auto-Response Intents", True, f"Found {len(auto_response_intents)} auto-response intents")
                
                # Check first auto-response intent configuration
                intent = auto_response_intents[0]
                required_fields = ['id', 'name', 'keywords', 'auto_respond']
                missing_fields = [field for field in required_fields if field not in intent]
                
                if missing_fields:
                    self.log_result("Intent Configuration", False, f"Missing fields: {missing_fields}", intent)
                    return False
                else:
                    self.log_result("Intent Configuration", True, f"Intent properly configured: {intent['name']}")
            else:
                self.log_result("Auto-Response Intents", False, "No auto-response intents found")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Intent Management", False, f"Exception: {str(e)}")
            return False
    
    def test_template_system(self):
        """Test Template System"""
        print("\n🧪 Testing Template System")
        
        try:
            # Get templates
            response = self.session.get(f"{BASE_URL}/templates")
            
            if response.status_code != 200:
                self.log_result("Templates GET", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            self.log_result("Templates GET", True, f"Found {len(templates)} templates")
            
            # Check for auto-response templates
            auto_response_templates = [t for t in templates if t.get('type') == 'auto_response' or 'auto' in t.get('name', '').lower()]
            
            if auto_response_templates:
                self.log_result("Auto-Response Templates", True, f"Found {len(auto_response_templates)} auto-response templates")
                
                # Check template structure
                template = auto_response_templates[0]
                required_fields = ['id', 'name', 'subject', 'content']
                missing_fields = [field for field in required_fields if field not in template]
                
                if missing_fields:
                    self.log_result("Template Structure", False, f"Missing fields: {missing_fields}", template)
                    return False
                else:
                    # Check for personalization placeholders
                    content = template.get('content', '')
                    subject = template.get('subject', '')
                    
                    placeholders_found = []
                    common_placeholders = ['{{first_name}}', '{{last_name}}', '{{company}}']
                    
                    for placeholder in common_placeholders:
                        if placeholder in content or placeholder in subject:
                            placeholders_found.append(placeholder)
                    
                    if placeholders_found:
                        self.log_result("Template Personalization", True, f"Found placeholders: {placeholders_found}")
                    else:
                        self.log_result("Template Personalization", False, "No personalization placeholders found")
                    
                    self.log_result("Template Structure", True, f"Template properly structured: {template['name']}")
            else:
                self.log_result("Auto-Response Templates", False, "No auto-response templates found")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Template System", False, f"Exception: {str(e)}")
            return False
    
    def test_database_connection(self):
        """Test Database Connection"""
        print("\n🧪 Testing Database Connection")
        
        try:
            # Test multiple endpoints to verify database connectivity
            endpoints_to_test = [
                ("/campaigns", "Campaigns"),
                ("/prospects", "Prospects"),
                ("/lists", "Lists"),
                ("/templates", "Templates"),
                ("/intents", "Intents"),
                ("/email-providers", "Email Providers")
            ]
            
            all_passed = True
            
            for endpoint, name in endpoints_to_test:
                response = self.session.get(f"{BASE_URL}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result(f"Database {name}", True, f"Retrieved {len(data)} records")
                    elif isinstance(data, dict) and 'industries' in data:  # Special case for industries
                        self.log_result(f"Database {name}", True, f"Retrieved {data.get('total_count', 0)} records")
                    else:
                        self.log_result(f"Database {name}", True, "Data retrieved successfully")
                else:
                    self.log_result(f"Database {name}", False, f"HTTP {response.status_code}")
                    all_passed = False
            
            if all_passed:
                self.log_result("Database Connection", True, "All database endpoints accessible")
            else:
                self.log_result("Database Connection", False, "Some database endpoints failed")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Database Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_groq_ai_integration(self):
        """Test Groq AI Integration"""
        print("\n🧪 Testing Groq AI Integration")
        
        try:
            # Test AI classification service
            test_email = {
                "subject": "Interested in your product",
                "content": "Hi, I'm very interested in your product and would like to know more about pricing and features. Can we schedule a demo?"
            }
            
            response = self.session.post(f"{BASE_URL}/email-processing/test-classification", json=test_email)
            
            if response.status_code != 200:
                self.log_result("Groq AI Classification", False, f"HTTP {response.status_code}", response.text)
                return False
            
            classification_result = response.json()
            
            # Check for required fields in AI response
            required_fields = ['classified_intents', 'sentiment_analysis']
            missing_fields = [field for field in required_fields if field not in classification_result]
            
            if missing_fields:
                self.log_result("Groq AI Response Structure", False, f"Missing fields: {missing_fields}", classification_result)
                return False
            
            # Check classified intents
            intents = classification_result.get('classified_intents', [])
            if intents:
                # Check confidence scores
                for intent in intents:
                    if 'confidence' not in intent:
                        self.log_result("Groq AI Confidence Scores", False, "Missing confidence score", intent)
                        return False
                    
                    confidence = intent.get('confidence', 0)
                    if confidence > 0.5:  # Good confidence threshold
                        self.log_result("Groq AI Classification Quality", True, f"High confidence classification: {confidence}")
                    else:
                        self.log_result("Groq AI Classification Quality", False, f"Low confidence classification: {confidence}")
                
                self.log_result("Groq AI Intent Classification", True, f"Classified {len(intents)} intents")
            else:
                self.log_result("Groq AI Intent Classification", False, "No intents classified")
                return False
            
            # Check sentiment analysis
            sentiment = classification_result.get('sentiment_analysis', {})
            if sentiment and 'sentiment' in sentiment:
                self.log_result("Groq AI Sentiment Analysis", True, f"Sentiment: {sentiment['sentiment']}")
            else:
                self.log_result("Groq AI Sentiment Analysis", False, "No sentiment analysis")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Groq AI Integration", False, f"Exception: {str(e)}")
            return False
    
    def test_service_management(self):
        """Test Service Management (start/stop services)"""
        print("\n🧪 Testing Service Management")
        
        try:
            # Test start all services
            response = self.session.post(f"{BASE_URL}/services/start-all")
            
            if response.status_code != 200:
                self.log_result("Start All Services", False, f"HTTP {response.status_code}", response.text)
                return False
            
            start_result = response.json()
            self.log_result("Start All Services", True, "Services start initiated")
            
            # Wait a moment and check status
            import time
            time.sleep(2)
            
            response = self.session.get(f"{BASE_URL}/services/status")
            if response.status_code == 200:
                status_data = response.json()
                services = status_data.get('services', {})
                
                running_services = 0
                for service_name, service_info in services.items():
                    if service_info.get('status') == 'running':
                        running_services += 1
                        self.log_result(f"{service_name} Running", True, "Service is running")
                    else:
                        self.log_result(f"{service_name} Running", False, f"Service status: {service_info.get('status')}")
                
                if running_services >= 2:  # Both services should be running
                    self.log_result("Service Management", True, f"{running_services} services running")
                else:
                    self.log_result("Service Management", False, f"Only {running_services} services running")
                    return False
            else:
                self.log_result("Service Status Check", False, f"HTTP {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Service Management", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_review_test(self):
        """Run comprehensive auto-responder review test"""
        print("🚀 AUTO-RESPONDER SYSTEM REVIEW TESTING - JANUARY 2025")
        print("=" * 80)
        print("Testing the specific functionality requested in the review:")
        print("1. Email Provider Configuration (particularly Gmail)")
        print("2. Auto Responder Services Status")
        print("3. IMAP Configuration")
        print("4. Intent Management")
        print("5. Template System")
        print("6. Database Connection")
        print("7. Groq AI Integration")
        print("=" * 80)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return False
        
        # Run all tests
        test_results = {
            "email_provider_configuration": self.test_email_provider_configuration(),
            "auto_responder_services_status": self.test_auto_responder_services_status(),
            "imap_configuration": self.test_imap_configuration(),
            "intent_management": self.test_intent_management(),
            "template_system": self.test_template_system(),
            "database_connection": self.test_database_connection(),
            "groq_ai_integration": self.test_groq_ai_integration(),
            "service_management": self.test_service_management()
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 AUTO-RESPONDER REVIEW TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL AUTO-RESPONDER TESTS PASSED")
            print("The automatic email responder system is fully operational and ready for Gmail integration")
        elif passed_tests >= total_tests * 0.75:  # 75% or more
            print(f"\n✅ MOSTLY FUNCTIONAL: {passed_tests}/{total_tests} tests passed")
            print("The auto-responder system is mostly working with minor issues")
        else:
            print(f"\n⚠️ SIGNIFICANT ISSUES: Only {passed_tests}/{total_tests} tests passed")
            print("The auto-responder system needs attention before Gmail integration")
        
        # Specific recommendations
        print("\n📋 RECOMMENDATIONS:")
        if not test_results["email_provider_configuration"]:
            print("- Configure Gmail email provider with proper SMTP/IMAP settings")
        if not test_results["auto_responder_services_status"]:
            print("- Ensure auto-responder services are running properly")
        if not test_results["imap_configuration"]:
            print("- Enable and configure IMAP monitoring for email providers")
        if not test_results["intent_management"]:
            print("- Set up auto-response intents with proper keywords")
        if not test_results["template_system"]:
            print("- Create auto-response templates with personalization")
        if not test_results["database_connection"]:
            print("- Fix database connectivity issues")
        if not test_results["groq_ai_integration"]:
            print("- Verify Groq AI API key and integration")
        if not test_results["service_management"]:
            print("- Fix service start/stop functionality")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = AutoResponderReviewTester()
    success = tester.run_comprehensive_review_test()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)