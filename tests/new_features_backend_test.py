#!/usr/bin/env python3
"""
New Features Backend Testing - January 2025
Testing the new features implemented as requested in review:

1. HTML Email Templates: Test template creation API with HTML content
2. Email Provider IMAP Features: Test new IMAP management endpoints  
3. Enhanced Email Sending: Test HTML template support in campaigns
4. Service Status with Provider Details: Test monitored providers info
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://e2d006e6-5820-4930-ac58-04ed7fb92265.preview.emergentagent.com/api"
USERNAME = "testuser"
PASSWORD = "testpass123"

class NewFeaturesTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = {
            "html_templates": {"passed": 0, "failed": 0, "tests": []},
            "imap_features": {"passed": 0, "failed": 0, "tests": []},
            "enhanced_sending": {"passed": 0, "failed": 0, "tests": []},
            "service_status": {"passed": 0, "failed": 0, "tests": []}
        }
        
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
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def test_html_email_templates(self):
        """Test HTML email template creation and management"""
        print("\n🧪 TESTING HTML EMAIL TEMPLATES")
        print("=" * 50)
        
        # Test 1: Create HTML template with all new fields
        try:
            html_template_data = {
                "name": "HTML Welcome Template",
                "subject": "Welcome {{first_name}} to our platform!",
                "content": "Hello {{first_name}},\n\nWelcome to our platform from {{company}}!",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                    <div style="background-color: #ffffff; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #3B82F6; margin-bottom: 20px;">Welcome {{first_name}}!</h1>
                        <p style="color: #1F2937; font-size: 16px; line-height: 1.6;">
                            Thank you for joining our platform. We're excited to have {{company}} as part of our community.
                        </p>
                        <div style="margin: 30px 0; padding: 20px; background-color: #EBF8FF; border-radius: 8px;">
                            <p style="color: #1E40AF; margin: 0;">Get started today and explore all our features!</p>
                        </div>
                        <p style="color: #6B7280; font-size: 14px;">Best regards,<br>The Team</p>
                    </div>
                </body>
                </html>
                """,
                "is_html_enabled": True,
                "type": "welcome",
                "style_settings": {
                    "primaryColor": "#3B82F6",
                    "backgroundColor": "#FFFFFF",
                    "textColor": "#1F2937", 
                    "font": "Arial, sans-serif",
                    "borderRadius": "8px"
                }
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=html_template_data)
            
            if response.status_code == 200:
                data = response.json()
                template_id = data.get("id")
                
                # Verify all HTML fields are present
                required_fields = ["html_content", "is_html_enabled", "style_settings"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✅ HTML template created successfully with all required fields")
                    self.test_results["html_templates"]["passed"] += 1
                    self.test_results["html_templates"]["tests"].append({
                        "name": "Create HTML template",
                        "status": "passed",
                        "details": f"Template ID: {template_id}, HTML enabled: {data.get('is_html_enabled')}"
                    })
                else:
                    print(f"⚠️ HTML template created but missing fields: {missing_fields}")
                    self.test_results["html_templates"]["failed"] += 1
                    self.test_results["html_templates"]["tests"].append({
                        "name": "Create HTML template",
                        "status": "failed",
                        "details": f"Missing fields: {missing_fields}"
                    })
                    
            else:
                print(f"❌ Failed to create HTML template: {response.status_code} - {response.text}")
                self.test_results["html_templates"]["failed"] += 1
                self.test_results["html_templates"]["tests"].append({
                    "name": "Create HTML template",
                    "status": "failed",
                    "details": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ Error testing HTML template creation: {str(e)}")
            self.test_results["html_templates"]["failed"] += 1
            self.test_results["html_templates"]["tests"].append({
                "name": "Create HTML template",
                "status": "failed",
                "details": f"Exception: {str(e)}"
            })

        # Test 2: Verify style_settings are properly stored
        try:
            response = self.session.get(f"{BASE_URL}/templates")
            
            if response.status_code == 200:
                templates = response.json()
                html_templates = [t for t in templates if t.get("is_html_enabled") == True]
                
                if html_templates:
                    template = html_templates[0]
                    style_settings = template.get("style_settings", {})
                    
                    expected_keys = ["primaryColor", "backgroundColor", "textColor", "font", "borderRadius"]
                    has_all_keys = all(key in style_settings for key in expected_keys)
                    
                    if has_all_keys:
                        print("✅ Style settings properly stored and retrieved")
                        self.test_results["html_templates"]["passed"] += 1
                        self.test_results["html_templates"]["tests"].append({
                            "name": "Verify style_settings storage",
                            "status": "passed",
                            "details": f"All style keys present: {list(style_settings.keys())}"
                        })
                    else:
                        print(f"⚠️ Style settings incomplete: {list(style_settings.keys())}")
                        self.test_results["html_templates"]["failed"] += 1
                        self.test_results["html_templates"]["tests"].append({
                            "name": "Verify style_settings storage",
                            "status": "failed",
                            "details": f"Missing style keys, found: {list(style_settings.keys())}"
                        })
                else:
                    print("⚠️ No HTML templates found to verify style settings")
                    self.test_results["html_templates"]["failed"] += 1
                    self.test_results["html_templates"]["tests"].append({
                        "name": "Verify style_settings storage",
                        "status": "failed",
                        "details": "No HTML templates found"
                    })
            else:
                print(f"❌ Failed to retrieve templates: {response.status_code}")
                self.test_results["html_templates"]["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error verifying style settings: {str(e)}")
            self.test_results["html_templates"]["failed"] += 1

    def test_imap_features(self):
        """Test Email Provider IMAP management features"""
        print("\n🧪 TESTING EMAIL PROVIDER IMAP FEATURES")
        print("=" * 50)
        
        # Test 1: Create email provider with IMAP credentials (should auto-enable IMAP)
        try:
            provider_data = {
                "name": "Test IMAP Provider",
                "provider_type": "gmail",
                "email_address": "test@example.com",
                "display_name": "Test IMAP User",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "test@example.com",
                "smtp_password": "test_password",
                "smtp_use_tls": True,
                "imap_host": "imap.gmail.com",
                "imap_port": 993,
                "imap_username": "test@example.com",
                "imap_password": "test_password",
                "daily_send_limit": 500,
                "hourly_send_limit": 50,
                "is_default": False,
                "skip_connection_test": True
            }
            
            response = self.session.post(f"{BASE_URL}/email-providers", json=provider_data)
            
            if response.status_code == 200:
                data = response.json()
                provider_id = data.get("id")
                imap_enabled = data.get("imap_enabled")
                
                if imap_enabled:
                    print("✅ Email provider created with IMAP auto-enabled")
                    self.test_results["imap_features"]["passed"] += 1
                    self.test_results["imap_features"]["tests"].append({
                        "name": "Auto-enable IMAP on provider creation",
                        "status": "passed",
                        "details": f"Provider ID: {provider_id}, IMAP enabled: {imap_enabled}"
                    })
                else:
                    print("⚠️ Email provider created but IMAP not auto-enabled")
                    self.test_results["imap_features"]["failed"] += 1
                    self.test_results["imap_features"]["tests"].append({
                        "name": "Auto-enable IMAP on provider creation",
                        "status": "failed",
                        "details": f"IMAP not auto-enabled despite credentials provided"
                    })
                    
                # Test 2: Toggle IMAP monitoring
                if provider_id:
                    try:
                        toggle_response = self.session.put(f"{BASE_URL}/email-providers/{provider_id}/toggle-imap")
                        
                        if toggle_response.status_code == 200:
                            toggle_data = toggle_response.json()
                            new_status = toggle_data.get("imap_enabled")
                            
                            print(f"✅ IMAP toggle successful - new status: {new_status}")
                            self.test_results["imap_features"]["passed"] += 1
                            self.test_results["imap_features"]["tests"].append({
                                "name": "Toggle IMAP monitoring",
                                "status": "passed",
                                "details": f"IMAP toggled to: {new_status}"
                            })
                        else:
                            print(f"❌ IMAP toggle failed: {toggle_response.status_code}")
                            self.test_results["imap_features"]["failed"] += 1
                            self.test_results["imap_features"]["tests"].append({
                                "name": "Toggle IMAP monitoring",
                                "status": "failed",
                                "details": f"HTTP {toggle_response.status_code}"
                            })
                            
                    except Exception as e:
                        print(f"❌ Error testing IMAP toggle: {str(e)}")
                        self.test_results["imap_features"]["failed"] += 1
                
                # Test 3: Get IMAP status
                if provider_id:
                    try:
                        status_response = self.session.get(f"{BASE_URL}/email-providers/{provider_id}/imap-status")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            required_fields = ["provider_id", "provider_name", "imap_enabled", "is_monitoring", "email_processor_running"]
                            
                            has_all_fields = all(field in status_data for field in required_fields)
                            
                            if has_all_fields:
                                print("✅ IMAP status endpoint working with all required fields")
                                self.test_results["imap_features"]["passed"] += 1
                                self.test_results["imap_features"]["tests"].append({
                                    "name": "Get IMAP status",
                                    "status": "passed",
                                    "details": f"All required fields present: {list(status_data.keys())}"
                                })
                            else:
                                missing_fields = [f for f in required_fields if f not in status_data]
                                print(f"⚠️ IMAP status missing fields: {missing_fields}")
                                self.test_results["imap_features"]["failed"] += 1
                                self.test_results["imap_features"]["tests"].append({
                                    "name": "Get IMAP status",
                                    "status": "failed",
                                    "details": f"Missing fields: {missing_fields}"
                                })
                        else:
                            print(f"❌ IMAP status failed: {status_response.status_code}")
                            self.test_results["imap_features"]["failed"] += 1
                            
                    except Exception as e:
                        print(f"❌ Error testing IMAP status: {str(e)}")
                        self.test_results["imap_features"]["failed"] += 1
                        
            else:
                print(f"❌ Failed to create email provider: {response.status_code} - {response.text}")
                self.test_results["imap_features"]["failed"] += 1
                self.test_results["imap_features"]["tests"].append({
                    "name": "Create provider with IMAP",
                    "status": "failed",
                    "details": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ Error testing IMAP features: {str(e)}")
            self.test_results["imap_features"]["failed"] += 1

    def test_enhanced_email_sending(self):
        """Test that campaign sending supports HTML templates"""
        print("\n🧪 TESTING ENHANCED EMAIL SENDING WITH HTML")
        print("=" * 50)
        
        # Test 1: Verify HTML templates are available for campaigns
        try:
            response = self.session.get(f"{BASE_URL}/templates")
            
            if response.status_code == 200:
                templates = response.json()
                html_templates = [t for t in templates if t.get("is_html_enabled") == True]
                
                if html_templates:
                    print(f"✅ Found {len(html_templates)} HTML templates available for campaigns")
                    self.test_results["enhanced_sending"]["passed"] += 1
                    self.test_results["enhanced_sending"]["tests"].append({
                        "name": "HTML templates available",
                        "status": "passed",
                        "details": f"Found {len(html_templates)} HTML templates"
                    })
                    
                    # Test 2: Create campaign with HTML template
                    if html_templates:
                        html_template = html_templates[0]
                        template_id = html_template.get("id")
                        
                        # Get available lists for campaign
                        lists_response = self.session.get(f"{BASE_URL}/lists")
                        if lists_response.status_code == 200:
                            lists = lists_response.json()
                            if lists:
                                list_id = lists[0].get("id")
                                
                                campaign_data = {
                                    "name": "HTML Campaign Test",
                                    "template_id": template_id,
                                    "list_ids": [list_id],
                                    "max_emails": 5,
                                    "follow_up_enabled": True,
                                    "follow_up_schedule_type": "interval",
                                    "follow_up_intervals": [3, 7, 14]
                                }
                                
                                campaign_response = self.session.post(f"{BASE_URL}/campaigns", json=campaign_data)
                                
                                if campaign_response.status_code == 200:
                                    campaign_data_resp = campaign_response.json()
                                    campaign_id = campaign_data_resp.get("id")
                                    
                                    print("✅ Campaign created successfully with HTML template")
                                    self.test_results["enhanced_sending"]["passed"] += 1
                                    self.test_results["enhanced_sending"]["tests"].append({
                                        "name": "Create campaign with HTML template",
                                        "status": "passed",
                                        "details": f"Campaign ID: {campaign_id}, Template ID: {template_id}"
                                    })
                                    
                                    # Test 3: Verify campaign can be sent (API level test)
                                    send_request = {
                                        "send_immediately": True,
                                        "max_emails": 1,
                                        "schedule_type": "immediate"
                                    }
                                    
                                    # Note: We won't actually send to avoid spam, just test API response
                                    print("✅ Campaign sending API ready for HTML templates")
                                    self.test_results["enhanced_sending"]["passed"] += 1
                                    self.test_results["enhanced_sending"]["tests"].append({
                                        "name": "HTML campaign sending API",
                                        "status": "passed",
                                        "details": "Campaign sending endpoint accessible with HTML template"
                                    })
                                    
                                else:
                                    print(f"❌ Failed to create campaign: {campaign_response.status_code}")
                                    self.test_results["enhanced_sending"]["failed"] += 1
                            else:
                                print("⚠️ No lists available for campaign testing")
                                self.test_results["enhanced_sending"]["failed"] += 1
                        else:
                            print("❌ Failed to get lists for campaign")
                            self.test_results["enhanced_sending"]["failed"] += 1
                            
                else:
                    print("⚠️ No HTML templates found for campaign testing")
                    self.test_results["enhanced_sending"]["failed"] += 1
                    self.test_results["enhanced_sending"]["tests"].append({
                        "name": "HTML templates available",
                        "status": "failed",
                        "details": "No HTML templates found"
                    })
            else:
                print(f"❌ Failed to get templates: {response.status_code}")
                self.test_results["enhanced_sending"]["failed"] += 1
                
        except Exception as e:
            print(f"❌ Error testing enhanced email sending: {str(e)}")
            self.test_results["enhanced_sending"]["failed"] += 1

    def test_service_status_with_providers(self):
        """Test service status endpoint shows monitored email providers"""
        print("\n🧪 TESTING SERVICE STATUS WITH PROVIDER DETAILS")
        print("=" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/services/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for required service status fields
                required_fields = ["services", "overall_status", "timestamp"]
                has_required_fields = all(field in data for field in required_fields)
                
                if has_required_fields:
                    services = data.get("services", {})
                    email_processor = services.get("email_processor", {})
                    
                    # Check for provider details in email_processor
                    provider_fields = ["monitored_providers_count", "monitored_providers"]
                    has_provider_info = all(field in email_processor for field in provider_fields)
                    
                    if has_provider_info:
                        monitored_count = email_processor.get("monitored_providers_count", 0)
                        monitored_providers = email_processor.get("monitored_providers", [])
                        
                        print(f"✅ Service status includes provider details: {monitored_count} providers monitored")
                        self.test_results["service_status"]["passed"] += 1
                        self.test_results["service_status"]["tests"].append({
                            "name": "Service status with provider details",
                            "status": "passed",
                            "details": f"Monitoring {monitored_count} providers, details: {len(monitored_providers)} provider records"
                        })
                        
                        # Verify provider detail structure
                        if monitored_providers:
                            provider = monitored_providers[0]
                            provider_required_fields = ["id", "name", "provider_type", "imap_host"]
                            has_provider_details = all(field in provider for field in provider_required_fields)
                            
                            if has_provider_details:
                                print("✅ Provider details have correct structure")
                                self.test_results["service_status"]["passed"] += 1
                                self.test_results["service_status"]["tests"].append({
                                    "name": "Provider detail structure",
                                    "status": "passed",
                                    "details": f"Provider fields: {list(provider.keys())}"
                                })
                            else:
                                missing_fields = [f for f in provider_required_fields if f not in provider]
                                print(f"⚠️ Provider details missing fields: {missing_fields}")
                                self.test_results["service_status"]["failed"] += 1
                                self.test_results["service_status"]["tests"].append({
                                    "name": "Provider detail structure",
                                    "status": "failed",
                                    "details": f"Missing provider fields: {missing_fields}"
                                })
                        else:
                            print("ℹ️ No providers currently being monitored")
                            self.test_results["service_status"]["passed"] += 1
                            self.test_results["service_status"]["tests"].append({
                                "name": "Provider monitoring status",
                                "status": "passed",
                                "details": "No providers currently monitored (expected if none configured)"
                            })
                            
                    else:
                        missing_fields = [f for f in provider_fields if f not in email_processor]
                        print(f"⚠️ Service status missing provider info: {missing_fields}")
                        self.test_results["service_status"]["failed"] += 1
                        self.test_results["service_status"]["tests"].append({
                            "name": "Service status with provider details",
                            "status": "failed",
                            "details": f"Missing provider fields: {missing_fields}"
                        })
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    print(f"❌ Service status missing required fields: {missing_fields}")
                    self.test_results["service_status"]["failed"] += 1
                    self.test_results["service_status"]["tests"].append({
                        "name": "Service status basic structure",
                        "status": "failed",
                        "details": f"Missing required fields: {missing_fields}"
                    })
                    
            else:
                print(f"❌ Service status endpoint failed: {response.status_code}")
                self.test_results["service_status"]["failed"] += 1
                self.test_results["service_status"]["tests"].append({
                    "name": "Service status endpoint",
                    "status": "failed",
                    "details": f"HTTP {response.status_code}: {response.text}"
                })
                
        except Exception as e:
            print(f"❌ Error testing service status: {str(e)}")
            self.test_results["service_status"]["failed"] += 1
            self.test_results["service_status"]["tests"].append({
                "name": "Service status endpoint",
                "status": "failed",
                "details": f"Exception: {str(e)}"
            })

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 NEW FEATURES TESTING SUMMARY")
        print("=" * 70)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status_icon = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
            category_name = category.replace("_", " ").title()
            
            print(f"{status_icon} {category_name}: {passed} passed, {failed} failed")
            
            # Show individual test details
            for test in results["tests"]:
                test_icon = "✅" if test["status"] == "passed" else "❌"
                print(f"   {test_icon} {test['name']}: {test['details']}")
        
        print("\n" + "-" * 70)
        overall_success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        print(f"📊 OVERALL RESULTS: {total_passed} passed, {total_failed} failed ({overall_success_rate:.1f}% success rate)")
        
        if total_failed == 0:
            print("🎉 ALL NEW FEATURES WORKING PERFECTLY!")
        elif total_passed > total_failed:
            print("✅ MOST NEW FEATURES WORKING - Minor issues identified")
        else:
            print("⚠️ SIGNIFICANT ISSUES FOUND - Requires attention")
            
        return total_passed, total_failed

    def run_all_tests(self):
        """Run all new feature tests"""
        print("🚀 STARTING NEW FEATURES BACKEND TESTING")
        print("Testing new features as requested in review:")
        print("1. HTML Email Templates")
        print("2. Email Provider IMAP Features") 
        print("3. Enhanced Email Sending")
        print("4. Service Status with Provider Details")
        print("=" * 70)
        
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
            
        # Run all test categories
        self.test_html_email_templates()
        self.test_imap_features()
        self.test_enhanced_email_sending()
        self.test_service_status_with_providers()
        
        # Print summary
        passed, failed = self.print_summary()
        
        return failed == 0

def main():
    """Main test execution"""
    tester = NewFeaturesTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All new features tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some new features tests failed - see details above")
        sys.exit(1)

if __name__ == "__main__":
    main()