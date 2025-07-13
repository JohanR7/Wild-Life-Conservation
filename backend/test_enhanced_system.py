#!/usr/bin/env python3
"""
Test the enhanced audio classification system
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_detection_stats():
    """Test detection statistics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/detections/stats")
        if response.status_code == 200:
            print("✅ Detection stats endpoint working")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Detection stats failed")
            return False
    except Exception as e:
        print(f"❌ Detection stats error: {e}")
        return False

def test_animal_counts():
    """Test animal counts endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/wildlife/counts")
        if response.status_code == 200:
            print("✅ Animal counts endpoint working")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Animal counts failed")
            return False
    except Exception as e:
        print(f"❌ Animal counts error: {e}")
        return False

def test_recent_detections():
    """Test recent detections endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/detections/recent?limit=5")
        if response.status_code == 200:
            print("✅ Recent detections endpoint working")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Recent detections failed")
            return False
    except Exception as e:
        print(f"❌ Recent detections error: {e}")
        return False

def test_recording_status():
    """Test recording status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/live-recording/status")
        if response.status_code == 200:
            print("✅ Recording status endpoint working")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ Recording status failed")
            return False
    except Exception as e:
        print(f"❌ Recording status error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Enhanced Audio Classification System")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Detection Stats", test_detection_stats),
        ("Animal Counts", test_animal_counts),
        ("Recent Detections", test_recent_detections),
        ("Recording Status", test_recording_status),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n🎯 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️  Some tests failed. Check server status.")

if __name__ == "__main__":
    main()
