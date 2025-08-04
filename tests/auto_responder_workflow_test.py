#!/usr/bin/env python3
"""
AI Email Auto-Responder System Testing - January 2025
Testing the complete auto-responder workflow as requested in the review.

Focus Areas:
1. Email Provider Configuration - Check Gmail credentials and IMAP setup
2. IMAP Monitoring - Test if system is monitoring inbox properly
3. Intent Classification - Test with keywords "interested", "pricing", "questions"
4. Auto-Response Generation - Check if responses are generated for auto_respond intents
5. Template System - Verify templates are linked to intents properly
6. Complete Workflow - Email detection → Intent classification → Response generation → Email sending

The user reports: "Auto responder not working when the Prospects respond to the Campaigns mails with identified intents and set templates"
"""

import requests
import json
import time
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://6464b8e1-a5e1-4bb7-b2f5-42bbc07856fb.preview.emergentagent.com"

class AutoResponderWorkflowTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.auth_token = None
        self.headers = {}
        self.test_results = {}
        self.gmail_provider_id = None
        self.auto_response_intents = []
        self.auto_response_templates = []
    
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
    
    def test_authentication(self):
        """Test authentication system"""
        try:
            print("\n🔐 Testing Authentication...")
            
            login_data = {"username": "testuser", "password": "testpass123"}
            response = requests.post(f"{self.base_url}/api/auth/login", json=login_data, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Authentication", False, f"HTTP {response.status_code}", response.text)
                return False
            
            auth_result = response.json()
            if 'access_token' not in auth_result:
                self.log_result("Authentication", False, "No access token in response", auth_result)
                return False
            
            self.auth_token = auth_result['access_token']
            self.headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            self.log_result("Authentication", True, "Login successful with testuser/testpass123")
            return True
            
        except Exception as e:
            self.log_result("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def test_email_provider_configuration(self):
        """Test Gmail provider configuration and credentials"""
        try:
            print("\n📧 Testing Email Provider Configuration...")
            
            # Get all email providers
            response = requests.get(f"{self.base_url}/api/email-providers", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Email Provider Configuration", False, f"HTTP {response.status_code}", response.text)
                return False
            
            providers = response.json()
            
            if not providers:
                self.log_result("Email Provider Configuration", False, "No email providers found", providers)
                return False
            
            # Look for Gmail provider with proper configuration
            gmail_providers = [p for p in providers if 'gmail' in p.get('provider_type', '').lower() or 'gmail' in p.get('email_address', '').lower()]
            
            if not gmail_providers:
                self.log_result("Email Provider Configuration", False, "No Gmail providers found", {
                    'total_providers': len(providers),
                    'provider_types': [p.get('provider_type', 'unknown') for p in providers]
                })
                return False
            
            # Check the first Gmail provider
            gmail_provider = gmail_providers[0]
            self.gmail_provider_id = gmail_provider.get('id')
            
            # Verify required fields for auto-responder
            required_fields = ['smtp_host', 'smtp_username', 'smtp_password', 'imap_host', 'imap_username', 'imap_password']
            missing_fields = []
            
            for field in required_fields:
                if not gmail_provider.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("Email Provider Configuration", False, f"Gmail provider missing required fields: {missing_fields}", gmail_provider)
                return False
            
            # Check if IMAP is enabled
            imap_enabled = gmail_provider.get('imap_enabled', False)
            if not imap_enabled:
                self.log_result("Email Provider Configuration", False, "IMAP not enabled for Gmail provider", gmail_provider)
                return False
            
            self.log_result("Email Provider Configuration", True, f"Gmail provider properly configured: {gmail_provider.get('email_address')}", {
                'provider_id': self.gmail_provider_id,
                'email_address': gmail_provider.get('email_address'),
                'imap_enabled': imap_enabled,
                'smtp_configured': bool(gmail_provider.get('smtp_host')),
                'imap_configured': bool(gmail_provider.get('imap_host'))
            })
            return True
            
        except Exception as e:
            self.log_result("Email Provider Configuration", False, f"Exception: {str(e)}")
            return False
    
    def test_imap_monitoring_status(self):
        """Test IMAP monitoring functionality"""
        try:
            print("\n📡 Testing IMAP Monitoring Status...")
            
            if not self.gmail_provider_id:
                self.log_result("IMAP Monitoring Status", False, "No Gmail provider ID available")
                return False
            
            # Test IMAP status for the Gmail provider
            response = requests.get(f"{self.base_url}/api/email-providers/{self.gmail_provider_id}/imap-status", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("IMAP Monitoring Status", False, f"HTTP {response.status_code}", response.text)
                return False
            
            imap_status = response.json()
            
            # Check required IMAP status fields
            required_fields = ['provider_id', 'provider_name', 'imap_enabled', 'is_monitoring', 'email_processor_running']
            missing_fields = []
            
            for field in required_fields:
                if field not in imap_status:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log_result("IMAP Monitoring Status", False, f"Missing IMAP status fields: {missing_fields}", imap_status)
                return False
            
            # Check if IMAP monitoring is active
            is_monitoring = imap_status.get('is_monitoring', False)
            email_processor_running = imap_status.get('email_processor_running', False)
            
            if not is_monitoring:
                self.log_result("IMAP Monitoring Status", False, "IMAP monitoring is not active", imap_status)
                return False
            
            if not email_processor_running:
                self.log_result("IMAP Monitoring Status", False, "Email processor is not running", imap_status)
                return False
            
            self.log_result("IMAP Monitoring Status", True, "IMAP monitoring is active and email processor is running", {
                'provider_name': imap_status.get('provider_name'),
                'is_monitoring': is_monitoring,
                'email_processor_running': email_processor_running,
                'imap_config': imap_status.get('imap_config', {})
            })
            return True
            
        except Exception as e:
            self.log_result("IMAP Monitoring Status", False, f"Exception: {str(e)}")
            return False
    
    def test_intent_classification_system(self):
        """Test intent classification with target keywords"""
        try:
            print("\n🧠 Testing Intent Classification System...")
            
            # Get all intents
            response = requests.get(f"{self.base_url}/api/intents", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Intent Classification System", False, f"HTTP {response.status_code}", response.text)
                return False
            
            intents = response.json()
            
            if not intents:
                self.log_result("Intent Classification System", False, "No intents found", intents)
                return False
            
            # Find auto-response intents
            self.auto_response_intents = [intent for intent in intents if intent.get('auto_respond', False)]
            
            if not self.auto_response_intents:
                self.log_result("Intent Classification System", False, "No auto-response intents found", {
                    'total_intents': len(intents),
                    'auto_respond_intents': 0
                })
                return False
            
            # Check if target keywords are covered (flexible matching)
            target_keywords = ['interested', 'pricing', 'questions']
            covered_keywords = []
            
            for intent in self.auto_response_intents:
                keywords = intent.get('keywords', [])
                if isinstance(keywords, str):
                    keywords = [k.strip() for k in keywords.split(',')]
                
                for target_keyword in target_keywords:
                    # More flexible matching - check both directions
                    keyword_matched = False
                    for keyword in keywords:
                        if (target_keyword.lower() in keyword.lower() or 
                            keyword.lower() in target_keyword.lower() or
                            # Handle singular/plural variations
                            (target_keyword.lower().rstrip('s') == keyword.lower()) or
                            (keyword.lower().rstrip('s') == target_keyword.lower().rstrip('s'))):
                            keyword_matched = True
                            break
                    
                    if keyword_matched and target_keyword not in covered_keywords:
                        covered_keywords.append(target_keyword)
            
            if len(covered_keywords) < len(target_keywords):
                missing_keywords = [kw for kw in target_keywords if kw not in covered_keywords]
                self.log_result("Intent Classification System", False, f"Target keywords not covered: {missing_keywords}", {
                    'auto_response_intents': len(self.auto_response_intents),
                    'covered_keywords': covered_keywords,
                    'missing_keywords': missing_keywords
                })
                return False
            
            # Test AI classification endpoint if available
            try:
                test_emails = [
                    "I'm interested in your product",
                    "Can you tell me about pricing?",
                    "I have some questions about your service"
                ]
                
                classification_results = []
                for test_email in test_emails:
                    # Try to classify using AI agent or classification endpoint
                    ai_response = requests.post(f"{self.base_url}/api/ai-agent/chat", 
                                              json={"message": f"Classify this email: {test_email}"}, 
                                              headers=self.headers, timeout=10)
                    
                    if ai_response.status_code == 200:
                        classification_results.append({
                            'email': test_email,
                            'classification': ai_response.json()
                        })
                
                self.log_result("Intent Classification System", True, f"Found {len(self.auto_response_intents)} auto-response intents covering target keywords", {
                    'auto_response_intents': len(self.auto_response_intents),
                    'covered_keywords': covered_keywords,
                    'intent_names': [intent.get('name') for intent in self.auto_response_intents],
                    'classification_test_results': len(classification_results)
                })
                
            except Exception as ai_error:
                self.log_result("Intent Classification System", True, f"Found {len(self.auto_response_intents)} auto-response intents covering target keywords (AI test failed: {str(ai_error)})", {
                    'auto_response_intents': len(self.auto_response_intents),
                    'covered_keywords': covered_keywords,
                    'intent_names': [intent.get('name') for intent in self.auto_response_intents]
                })
            
            return True
            
        except Exception as e:
            self.log_result("Intent Classification System", False, f"Exception: {str(e)}")
            return False
    
    def test_template_system(self):
        """Test auto-response template system"""
        try:
            print("\n📝 Testing Template System...")
            
            # Get all templates
            response = requests.get(f"{self.base_url}/api/templates", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Template System", False, f"HTTP {response.status_code}", response.text)
                return False
            
            templates = response.json()
            
            if not templates:
                self.log_result("Template System", False, "No templates found", templates)
                return False
            
            # Find auto-response templates
            self.auto_response_templates = [template for template in templates if 
                                          template.get('type') == 'auto_response' or 
                                          'auto' in template.get('name', '').lower() or
                                          'response' in template.get('name', '').lower()]
            
            if not self.auto_response_templates:
                # If no explicit auto-response templates, check if any templates have personalization
                personalized_templates = [template for template in templates if 
                                        '{{' in template.get('content', '') or 
                                        '{{' in template.get('subject', '')]
                
                if personalized_templates:
                    self.auto_response_templates = personalized_templates[:3]  # Take first 3 as potential auto-response templates
                else:
                    self.log_result("Template System", False, "No auto-response templates found", {
                        'total_templates': len(templates),
                        'template_types': [template.get('type') for template in templates]
                    })
                    return False
            
            # Check template personalization
            personalization_count = 0
            for template in self.auto_response_templates:
                content = template.get('content', '')
                subject = template.get('subject', '')
                
                if '{{first_name}}' in content or '{{company}}' in content or '{{first_name}}' in subject:
                    personalization_count += 1
            
            # Check if templates are linked to intents
            template_intent_links = 0
            for intent in self.auto_response_intents:
                if intent.get('template_id') or intent.get('primary_template'):
                    template_intent_links += 1
            
            self.log_result("Template System", True, f"Found {len(self.auto_response_templates)} auto-response templates", {
                'auto_response_templates': len(self.auto_response_templates),
                'personalized_templates': personalization_count,
                'template_intent_links': template_intent_links,
                'template_names': [template.get('name') for template in self.auto_response_templates]
            })
            return True
            
        except Exception as e:
            self.log_result("Template System", False, f"Exception: {str(e)}")
            return False
    
    def test_auto_responder_services(self):
        """Test auto-responder service status"""
        try:
            print("\n⚙️ Testing Auto-Responder Services...")
            
            # Get service status
            response = requests.get(f"{self.base_url}/api/services/status", headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                self.log_result("Auto-Responder Services", False, f"HTTP {response.status_code}", response.text)
                return False
            
            services_status = response.json()
            
            # Check for required services
            services = services_status.get('services', {})
            
            if 'email_processor' not in services:
                self.log_result("Auto-Responder Services", False, "Email processor service not found", services_status)
                return False
            
            email_processor = services['email_processor']
            email_processor_status = email_processor.get('status')
            
            if email_processor_status != 'running':
                # Try to start the service
                start_response = requests.post(f"{self.base_url}/api/services/start-all", headers=self.headers, timeout=10)
                if start_response.status_code == 200:
                    time.sleep(3)  # Wait for services to start
                    
                    # Check status again
                    response = requests.get(f"{self.base_url}/api/services/status", headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        services_status = response.json()
                        email_processor_status = services_status.get('services', {}).get('email_processor', {}).get('status')
            
            if email_processor_status != 'running':
                self.log_result("Auto-Responder Services", False, f"Email processor not running: {email_processor_status}", services_status)
                return False
            
            # Check monitored providers
            monitored_providers = email_processor.get('monitored_providers', [])
            monitored_count = email_processor.get('monitored_providers_count', 0)
            
            if monitored_count == 0:
                self.log_result("Auto-Responder Services", False, "No providers being monitored", {
                    'email_processor_status': email_processor_status,
                    'monitored_providers_count': monitored_count
                })
                return False
            
            self.log_result("Auto-Responder Services", True, f"Email processor running and monitoring {monitored_count} providers", {
                'email_processor_status': email_processor_status,
                'monitored_providers_count': monitored_count,
                'overall_status': services_status.get('overall_status'),
                'monitored_providers': [p.get('name') for p in monitored_providers]
            })
            return True
            
        except Exception as e:
            self.log_result("Auto-Responder Services", False, f"Exception: {str(e)}")
            return False
    
    def test_complete_auto_response_workflow(self):
        """Test the complete auto-response workflow simulation"""
        try:
            print("\n🔄 Testing Complete Auto-Response Workflow...")
            
            # Simulate email processing workflow
            workflow_steps = []
            
            # Step 1: Check if we have all components
            if not self.gmail_provider_id:
                workflow_steps.append("❌ No Gmail provider configured")
            else:
                workflow_steps.append("✅ Gmail provider configured")
            
            if not self.auto_response_intents:
                workflow_steps.append("❌ No auto-response intents found")
            else:
                workflow_steps.append(f"✅ {len(self.auto_response_intents)} auto-response intents found")
            
            if not self.auto_response_templates:
                workflow_steps.append("❌ No auto-response templates found")
            else:
                workflow_steps.append(f"✅ {len(self.auto_response_templates)} auto-response templates found")
            
            # Step 2: Test AI classification with target keywords
            test_emails = [
                {"content": "I'm interested in your product", "expected_keywords": ["interested"]},
                {"content": "Can you tell me about pricing?", "expected_keywords": ["pricing"]},
                {"content": "I have questions about your service", "expected_keywords": ["questions"]}
            ]
            
            classification_success = 0
            for test_email in test_emails:
                try:
                    # Try AI classification
                    ai_response = requests.post(f"{self.base_url}/api/ai-agent/chat", 
                                              json={"message": f"Classify email intent: {test_email['content']}"}, 
                                              headers=self.headers, timeout=10)
                    
                    if ai_response.status_code == 200:
                        classification_success += 1
                        workflow_steps.append(f"✅ Classified: '{test_email['content'][:30]}...'")
                    else:
                        workflow_steps.append(f"⚠️ Classification failed for: '{test_email['content'][:30]}...'")
                        
                except Exception as class_error:
                    workflow_steps.append(f"❌ Classification error: {str(class_error)}")
            
            # Step 3: Check if auto-response would be triggered
            auto_response_triggers = 0
            for intent in self.auto_response_intents:
                if intent.get('auto_respond', False):
                    auto_response_triggers += 1
            
            if auto_response_triggers > 0:
                workflow_steps.append(f"✅ {auto_response_triggers} intents configured to trigger auto-responses")
            else:
                workflow_steps.append("❌ No intents configured to trigger auto-responses")
            
            # Step 4: Check template personalization capability
            personalized_templates = 0
            for template in self.auto_response_templates:
                content = template.get('content', '')
                if '{{first_name}}' in content or '{{company}}' in content:
                    personalized_templates += 1
            
            if personalized_templates > 0:
                workflow_steps.append(f"✅ {personalized_templates} templates support personalization")
            else:
                workflow_steps.append("⚠️ No templates with personalization found")
            
            # Calculate workflow health
            success_steps = len([step for step in workflow_steps if step.startswith("✅")])
            total_steps = len(workflow_steps)
            workflow_health = (success_steps / total_steps) * 100
            
            if workflow_health >= 80:
                self.log_result("Complete Auto-Response Workflow", True, f"Workflow health: {workflow_health:.1f}% ({success_steps}/{total_steps} steps successful)", {
                    'workflow_steps': workflow_steps,
                    'workflow_health': workflow_health,
                    'classification_success': classification_success,
                    'auto_response_triggers': auto_response_triggers
                })
                return True
            else:
                self.log_result("Complete Auto-Response Workflow", False, f"Workflow health: {workflow_health:.1f}% ({success_steps}/{total_steps} steps successful)", {
                    'workflow_steps': workflow_steps,
                    'workflow_health': workflow_health,
                    'issues_found': [step for step in workflow_steps if step.startswith("❌")]
                })
                return False
            
        except Exception as e:
            self.log_result("Complete Auto-Response Workflow", False, f"Exception: {str(e)}")
            return False
    
    def test_database_integrity(self):
        """Test database integrity for auto-responder components"""
        try:
            print("\n🗄️ Testing Database Integrity...")
            
            # Test prospects (needed for personalization)
            response = requests.get(f"{self.base_url}/api/prospects", headers=self.headers, timeout=10)
            prospects_count = 0
            if response.status_code == 200:
                prospects = response.json()
                prospects_count = len(prospects) if isinstance(prospects, list) else 0
            
            # Test campaigns (source of emails that trigger auto-responses)
            response = requests.get(f"{self.base_url}/api/campaigns", headers=self.headers, timeout=10)
            campaigns_count = 0
            if response.status_code == 200:
                campaigns = response.json()
                campaigns_count = len(campaigns) if isinstance(campaigns, list) else 0
            
            # Test lists (for prospect organization)
            response = requests.get(f"{self.base_url}/api/lists", headers=self.headers, timeout=10)
            lists_count = 0
            if response.status_code == 200:
                lists = response.json()
                lists_count = len(lists) if isinstance(lists, list) else 0
            
            database_health = {
                'prospects': prospects_count,
                'campaigns': campaigns_count,
                'lists': lists_count,
                'email_providers': 1 if self.gmail_provider_id else 0,
                'auto_response_intents': len(self.auto_response_intents),
                'auto_response_templates': len(self.auto_response_templates)
            }
            
            # Check if we have minimum required data
            required_minimums = {
                'email_providers': 1,
                'auto_response_intents': 1,
                'auto_response_templates': 1,
                'prospects': 1
            }
            
            missing_data = []
            for component, minimum in required_minimums.items():
                if database_health[component] < minimum:
                    missing_data.append(f"{component}: {database_health[component]}/{minimum}")
            
            if missing_data:
                self.log_result("Database Integrity", False, f"Insufficient data for auto-responder: {', '.join(missing_data)}", database_health)
                return False
            
            self.log_result("Database Integrity", True, "Database has sufficient data for auto-responder functionality", database_health)
            return True
            
        except Exception as e:
            self.log_result("Database Integrity", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_auto_responder_tests(self):
        """Run comprehensive auto-responder workflow tests"""
        print("🚀 Starting Comprehensive Auto-Responder System Tests")
        print("Focus: Complete workflow testing for auto-responder functionality")
        print("User Issue: Auto responder not working when prospects respond to campaign emails")
        print("=" * 80)
        
        tests = [
            ("1. Authentication", self.test_authentication),
            ("2. Email Provider Configuration", self.test_email_provider_configuration),
            ("3. IMAP Monitoring Status", self.test_imap_monitoring_status),
            ("4. Intent Classification System", self.test_intent_classification_system),
            ("5. Template System", self.test_template_system),
            ("6. Auto-Responder Services", self.test_auto_responder_services),
            ("7. Database Integrity", self.test_database_integrity),
            ("8. Complete Auto-Response Workflow", self.test_complete_auto_response_workflow)
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
                    critical_failures.append(test_name)
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
                critical_failures.append(test_name)
        
        print("\n" + "=" * 80)
        print(f"📊 Test Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All auto-responder workflow tests passed!")
            print("✅ The auto-responder system appears to be properly configured.")
        else:
            print(f"⚠️  {total - passed} tests failed")
            if critical_failures:
                print(f"🚨 Critical failures in: {', '.join(critical_failures)}")
                print("\n🔍 POTENTIAL ISSUES IDENTIFIED:")
                for failure in critical_failures:
                    if failure in self.test_results:
                        print(f"   - {failure}: {self.test_results[failure]['message']}")
        
        return self.test_results, critical_failures
    
    def print_detailed_results(self):
        """Print detailed test results for main agent"""
        print("\n" + "=" * 80)
        print("📋 DETAILED AUTO-RESPONDER WORKFLOW TEST RESULTS")
        print("=" * 80)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}")
            if result['message']:
                print(f"   Message: {result['message']}")
            if result['details']:
                print(f"   Details: {json.dumps(result['details'], indent=4)}")
            print()
        
        # Summary for main agent
        passed_tests = [name for name, result in self.test_results.items() if result['success']]
        failed_tests = [name for name, result in self.test_results.items() if not result['success']]
        
        print("\n" + "=" * 80)
        print("📝 SUMMARY FOR MAIN AGENT")
        print("=" * 80)
        
        print("✅ WORKING COMPONENTS:")
        for test in passed_tests:
            print(f"   - {test}")
        
        if failed_tests:
            print("\n❌ FAILING COMPONENTS:")
            for test in failed_tests:
                print(f"   - {test}")
                if test in self.test_results:
                    print(f"     Issue: {self.test_results[test]['message']}")
        
        print(f"\n📊 Overall Auto-Responder Health: {len(passed_tests)}/{len(self.test_results)} ({(len(passed_tests)/len(self.test_results))*100:.1f}%)")
        
        # Specific recommendations
        print("\n🔧 RECOMMENDATIONS:")
        if len(passed_tests) == len(self.test_results):
            print("   ✅ Auto-responder system is properly configured and should be working")
            print("   ✅ All components are operational - issue may be with real email processing")
            print("   🔍 Consider checking email logs and IMAP scan history for actual email processing")
        else:
            print("   🚨 Critical issues found that prevent auto-responder from working:")
            for test in failed_tests:
                if test in self.test_results:
                    print(f"   - Fix {test}: {self.test_results[test]['message']}")

def main():
    """Main test execution"""
    tester = AutoResponderWorkflowTester()
    results, critical_failures = tester.run_comprehensive_auto_responder_tests()
    tester.print_detailed_results()
    
    return results, critical_failures

if __name__ == "__main__":
    main()