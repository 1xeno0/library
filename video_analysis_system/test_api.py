#!/usr/bin/env python3
"""
Test script for the Patchwork Library Analyzer + Search API
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:5050"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_analyse_endpoint():
    """Test the video analysis endpoint"""
    print("\nTesting /analyse endpoint...")
    
    test_data = {
        "video_link": "https://renderer.ezr.lv/render/680876b27ed09a50637439a"
    }
    
    try:
        print("Sending analysis request...")
        response = requests.post(
            f"{BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Analysis successful!")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Analysis failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Analysis request failed: {e}")
        return None

def test_find_clips_endpoint():
    """Test the search endpoint"""
    print("\nTesting /find_clips endpoint...")
    
    # Test with search query
    test_data = {
        "search_query": "video",
        "tags": []
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/find_clips",
            headers={"Content-Type": "application/json"},
            json=test_data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Search successful!")
            print(json.dumps(result, indent=2))
            return True
        elif response.status_code == 404:
            print("No clips found (this is expected if no videos have been analyzed yet)")
            return True
        else:
            print(f"Search failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Search request failed: {e}")
        return False

def test_list_videos():
    """Test the list videos endpoint"""
    print("\nTesting /videos endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/videos")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['count']} videos in database")
            if result['videos']:
                print("Sample video:")
                print(json.dumps(result['videos'][0], indent=2))
            return True
        else:
            print(f"List videos failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"List videos request failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Patchwork Library Analyzer API Tests")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("❌ Health check failed - make sure the server is running")
        return
    
    print("✅ Health check passed")
    
    # Test list videos (should work even with empty database)
    if test_list_videos():
        print("✅ List videos endpoint working")
    else:
        print("❌ List videos endpoint failed")
    
    # Test search (should work even with empty database)
    if test_find_clips_endpoint():
        print("✅ Search endpoint working")
    else:
        print("❌ Search endpoint failed")
    
    # Test analysis (this will take longer due to video processing)
    print("\n⚠️  Video analysis test will take some time...")
    print("This involves downloading video, extracting frames, and AI analysis...")
    
    user_input = input("Do you want to run the analysis test? (y/n): ")
    if user_input.lower() == 'y':
        analysis_result = test_analyse_endpoint()
        if analysis_result:
            print("✅ Analysis endpoint working")
            
            # Test search again with the analyzed video
            print("\nTesting search with analyzed video...")
            if test_find_clips_endpoint():
                print("✅ Search with data working")
        else:
            print("❌ Analysis endpoint failed")
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 