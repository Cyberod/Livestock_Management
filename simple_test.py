#!/usr/bin/env python
"""
Simple End-to-End Testing Script for Livestock Management System
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livestock_management.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import *


def run_basic_tests():
    """Run basic functionality tests"""
    print("=" * 60)
    print("LIVESTOCK MANAGEMENT SYSTEM - BASIC TESTS")
    print("=" * 60)
    
    client = Client()
    passed = 0
    failed = 0
    
    # Test 1: Check data integrity
    print("\n1. Testing Data Integrity...")
    try:
        animal_types = AnimalType.objects.count()
        breeds = Breed.objects.count()
        feed_types = FeedType.objects.count()
        diseases = Disease.objects.count()
        symptoms = Symptom.objects.count()
        
        print(f"   Animal Types: {animal_types}")
        print(f"   Breeds: {breeds}")
        print(f"   Feed Types: {feed_types}")
        print(f"   Diseases: {diseases}")
        print(f"   Symptoms: {symptoms}")
        
        if all([animal_types > 0, breeds > 0, feed_types > 0, diseases > 0, symptoms > 0]):
            print("   PASS: All essential data present")
            passed += 1
        else:
            print("   FAIL: Missing essential data")
            failed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 2: Test homepage
    print("\n2. Testing Homepage...")
    try:
        response = client.get('/')
        if response.status_code == 200:
            print("   PASS: Homepage loads successfully")
            passed += 1
        else:
            print(f"   FAIL: Homepage status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 3: Test animal types API
    print("\n3. Testing Animal Types API...")
    try:
        response = client.get('/api/animal-types/')
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                print(f"   PASS: API returned {len(data)} animal types")
                passed += 1
            else:
                print("   FAIL: API returned empty data")
                failed += 1
        else:
            print(f"   FAIL: API status code {response.status_code}")
            failed += 1
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Test 4: Test modules pages
    modules = [
        ('/feeding/', 'Feeding Guide'),
        ('/disease/', 'Disease Monitor'), 
        ('/pricing/', 'Pricing Guide')
    ]
    
    print("\n4. Testing Module Pages...")
    for url, name in modules:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"   PASS: {name} page loads")
                passed += 1
            else:
                print(f"   FAIL: {name} status code {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"   FAIL: {name} - {e}")
            failed += 1
    
    # Test 5: Test with authenticated user
    print("\n5. Testing Authenticated User Flow...")
    try:
        # Create test user
        test_user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Login
        login_success = client.login(username='testuser', password='testpass123')
        if login_success:
            print("   PASS: User login successful")
            passed += 1
            
            # Test user livestock API
            response = client.get('/api/user/livestock/')
            if response.status_code == 200:
                print("   PASS: User livestock API working")
                passed += 1
            else:
                print(f"   FAIL: User livestock API status {response.status_code}")
                failed += 1
        else:
            print("   FAIL: User login failed")
            failed += 1
            
        # Cleanup
        test_user.delete()
        
    except Exception as e:
        print(f"   FAIL: {e}")
        failed += 1
    
    # Summary
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        print("\nALL TESTS PASSED! System is working correctly.")
    else:
        print(f"\n{failed} tests failed. Please review issues.")
    
    print("=" * 60)


if __name__ == '__main__':
    run_basic_tests()
