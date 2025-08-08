#!/usr/bin/env python
"""
End-to-End Testing Script for Livestock Management System
Tests all major functionality across feeding, disease monitoring, and pricing modules
"""

import os
import sys
import django
import json
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livestock_management.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from core.models import *


class EndToEndTestSuite:
    """Comprehensive end-to-end test suite"""
    
    def __init__(self):
        self.client = Client()
        self.base_url = 'http://127.0.0.1:8000'
        self.test_user = None
        self.test_livestock = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def run_all_tests(self):
        """Run all end-to-end tests"""
        print("=" * 80)
        print("🧪 LIVESTOCK MANAGEMENT SYSTEM - END-TO-END TESTING")
        print("=" * 80)
        
        try:
            # Setup test data
            self.setup_test_data()
            
            # Test modules
            self.test_authentication()
            self.test_dashboard()
            self.test_feeding_module()
            self.test_disease_monitoring()
            self.test_pricing_module()
            self.test_api_endpoints()
            
            # Cleanup
            self.cleanup_test_data()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
            self.failed_tests += 1
        
        # Print summary
        self.print_summary()
    
    def setup_test_data(self):
        """Setup test data for end-to-end testing"""
        print("\n📋 Setting up test data...")
        
        try:
            # Create test user
            self.test_user = User.objects.create_user(
                username='testfarmer',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='Farmer'
            )
            
            # Ensure basic data exists (run seed_data if needed)
            if not AnimalType.objects.exists():
                from django.core.management import call_command
                call_command('seed_data')
            
            print("✅ Test data setup completed")
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Failed to setup test data: {e}")
            self.failed_tests += 1
            raise
    
    def test_authentication(self):
        """Test authentication flow"""
        print("\n🔐 Testing Authentication...")
        
        # Test login
        login_successful = self.client.login(username='testfarmer', password='testpass123')
        if login_successful:
            print("✅ User login successful")
            self.passed_tests += 1
        else:
            print("❌ User login failed")
            self.failed_tests += 1
    
    def test_dashboard(self):
        """Test dashboard functionality"""
        print("\n📊 Testing Dashboard...")
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                print("✅ Dashboard loads successfully")
                self.passed_tests += 1
                
                # Check if dashboard contains expected elements
                content = response.content.decode()
                if 'Welcome back' in content:
                    print("✅ Dashboard shows personalized welcome")
                    self.passed_tests += 1
                else:
                    print("❌ Dashboard missing personalized content")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Dashboard failed to load: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Dashboard test failed: {e}")
            self.failed_tests += 1
    
    def test_feeding_module(self):
        """Test feeding module functionality"""
        print("\n🥬 Testing Feeding Module...")
        
        try:
            # Test feeding guide page
            response = self.client.get('/feeding/')
            if response.status_code == 200:
                print("✅ Feeding guide page loads")
                self.passed_tests += 1
            else:
                print(f"❌ Feeding guide page failed: {response.status_code}")
                self.failed_tests += 1
            
            # Test feeding recommendations API
            api_data = {
                'animal_type_id': 1,  # Assuming Cattle is ID 1
                'age_months': 12,
                'weight_kg': 200,
                'purpose': 'MEAT'
            }
            
            response = self.client.post(
                '/api/feeding/recommendations/',
                data=json.dumps(api_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'recommendations' in data:
                    print("✅ Feeding recommendations API working")
                    self.passed_tests += 1
                else:
                    print("❌ Feeding recommendations API returns invalid data")
                    self.failed_tests += 1
            else:
                print(f"❌ Feeding recommendations API failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Feeding module test failed: {e}")
            self.failed_tests += 1
    
    def test_disease_monitoring(self):
        """Test disease monitoring functionality"""
        print("\n🏥 Testing Disease Monitoring...")
        
        try:
            # Test disease monitor page
            response = self.client.get('/disease/')
            if response.status_code == 200:
                print("✅ Disease monitor page loads")
                self.passed_tests += 1
            else:
                print(f"❌ Disease monitor page failed: {response.status_code}")
                self.failed_tests += 1
            
            # Test symptom analysis API
            api_data = {
                'animal_type_id': 1,
                'symptoms': [1, 2]  # Assuming some symptom IDs exist
            }
            
            response = self.client.post(
                '/api/disease/analyze-symptoms/',
                data=json.dumps(api_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'disease_results' in data:
                    print("✅ Disease analysis API working")
                    self.passed_tests += 1
                else:
                    print("❌ Disease analysis API returns invalid data")
                    self.failed_tests += 1
            else:
                print(f"❌ Disease analysis API failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Disease monitoring test failed: {e}")
            self.failed_tests += 1
    
    def test_pricing_module(self):
        """Test pricing module functionality"""
        print("\n💰 Testing Pricing Module...")
        
        try:
            # Test pricing guide page
            response = self.client.get('/pricing/')
            if response.status_code == 200:
                print("✅ Pricing guide page loads")
                self.passed_tests += 1
            else:
                print(f"❌ Pricing guide page failed: {response.status_code}")
                self.failed_tests += 1
            
            # Test market price analysis API
            api_data = {
                'animal_type_id': 1,
                'location': 'Test Market',
                'quality_grade': 'GOOD'
            }
            
            response = self.client.post(
                '/api/pricing/analyze-market/',
                data=json.dumps(api_data),
                content_type='application/json'
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'current_price_per_kg' in data:
                    print("✅ Market price analysis API working")
                    self.passed_tests += 1
                else:
                    print("❌ Market price analysis API returns invalid data")
                    self.failed_tests += 1
            else:
                print(f"❌ Market price analysis API failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Pricing module test failed: {e}")
            self.failed_tests += 1
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        print("\n🔌 Testing API Endpoints...")
        
        endpoints_to_test = [
            ('/api/animal-types/', 'Animal Types API'),
            ('/api/breeds/', 'Breeds API'),
            ('/api/feed-types/', 'Feed Types API'),
            ('/api/symptoms/', 'Symptoms API'),
            ('/api/diseases/', 'Diseases API'),
            ('/api/user/livestock/', 'User Livestock API'),
        ]
        
        for endpoint, name in endpoints_to_test:
            try:
                response = self.client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {name} working")
                    self.passed_tests += 1
                else:
                    print(f"❌ {name} failed: {response.status_code}")
                    self.failed_tests += 1
            except Exception as e:
                print(f"❌ {name} error: {e}")
                self.failed_tests += 1
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            if self.test_user:
                self.test_user.delete()
            print("✅ Test data cleaned up")
            self.passed_tests += 1
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
            self.failed_tests += 1
    
    def print_summary(self):
        """Print test summary"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        else:
            print(f"\n⚠️  {self.failed_tests} tests failed. Please review and fix issues.")
        
        print("=" * 80)


def run_data_integrity_tests():
    """Test data integrity"""
    print("\n🔍 Testing Data Integrity...")
    
    try:
        # Check if essential data exists
        animal_types = AnimalType.objects.count()
        breeds = Breed.objects.count()
        feed_types = FeedType.objects.count()
        diseases = Disease.objects.count()
        symptoms = Symptom.objects.count()
        
        print(f"📊 Data counts:")
        print(f"   Animal Types: {animal_types}")
        print(f"   Breeds: {breeds}")
        print(f"   Feed Types: {feed_types}")
        print(f"   Diseases: {diseases}")
        print(f"   Symptoms: {symptoms}")
        
        if all([animal_types > 0, breeds > 0, feed_types > 0, diseases > 0, symptoms > 0]):
            print("✅ All essential data present")
            return True
        else:
            print("❌ Missing essential data - run 'python manage.py seed_data'")
            return False
            
    except Exception as e:
        print(f"❌ Data integrity check failed: {e}")
        return False


def main():
    """Main test runner"""
    print("Starting Livestock Management System E2E Tests...")
    
    # Check data integrity first
    if not run_data_integrity_tests():
        print("\n❌ Data integrity check failed. Please run 'python manage.py seed_data' first.")
        return
    
    # Run comprehensive tests
    test_suite = EndToEndTestSuite()
    test_suite.run_all_tests()


if __name__ == '__main__':
    main()
