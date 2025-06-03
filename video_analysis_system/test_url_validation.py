#!/usr/bin/env python3
"""
Test script for URL validation and error handling improvements
"""

import requests
import json
import sys

def test_api_endpoint(base_url="http://localhost:5051"):
    """Test the /analyse endpoint with various URL types"""
    
    test_cases = [
        {
            "name": "Invalid URL - 404 Example",
            "url": "https://example.com/coscu-ace.mp4",
            "expected_status": 400,
            "description": "Should return 400 with helpful error message for 404 URLs"
        },
        {
            "name": "Invalid URL - Non-existent domain",
            "url": "https://this-domain-does-not-exist-12345.com/video.mp4",
            "expected_status": 400,
            "description": "Should return 400 for non-existent domains"
        },
        {
            "name": "Invalid URL - Not a video",
            "url": "https://google.com",
            "expected_status": 400,
            "description": "Should return 400 for non-video URLs"
        },
        {
            "name": "Valid YouTube URL",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expected_status": 200,
            "description": "Should work with valid YouTube URLs"
        },
        {
            "name": "Empty URL",
            "url": "",
            "expected_status": 400,
            "description": "Should return 400 for empty URLs"
        }
    ]
    
    print("🧪 Testing URL Validation and Error Handling")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: HTTP {test_case['expected_status']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/analyse",
                json={"video_link": test_case['url']},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   Result: HTTP {response.status_code}")
            
            # Parse response
            try:
                response_data = response.json()
                if response.status_code == test_case['expected_status']:
                    print(f"   ✅ PASS - Got expected status code")
                    if 'error' in response_data:
                        print(f"   📝 Error message: {response_data['error']}")
                    elif 'title' in response_data:
                        print(f"   📝 Success: {response_data['title']}")
                else:
                    print(f"   ❌ FAIL - Expected {test_case['expected_status']}, got {response.status_code}")
                    if 'error' in response_data:
                        print(f"   📝 Error: {response_data['error']}")
                        
            except json.JSONDecodeError:
                print(f"   ⚠️  Invalid JSON response: {response.text[:100]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {str(e)}")
        
        print("-" * 40)

def test_direct_analyzer():
    """Test the VideoAnalyzer class directly"""
    print("\n🔬 Testing VideoAnalyzer Class Directly")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from analyse import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        
        test_urls = [
            "https://example.com/nonexistent.mp4",
            "https://google.com",
            "not-a-url",
            ""
        ]
        
        for url in test_urls:
            print(f"\nTesting URL: {url}")
            try:
                is_valid, message = analyzer.validate_video_url(url)
                print(f"Valid: {is_valid}")
                print(f"Message: {message}")
            except Exception as e:
                print(f"Error: {str(e)}")
                
    except ImportError as e:
        print(f"❌ Could not import VideoAnalyzer: {e}")
        print("Make sure you're running this from the video_analysis_system directory")

def main():
    """Main test function"""
    print("🚀 Video Analysis System - URL Validation Tests")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:5051/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running, testing endpoints...")
            test_api_endpoint()
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ API is not running. Start it with: python app.py")
        print("Testing VideoAnalyzer class directly instead...")
        test_direct_analyzer()
        return
    
    # Also test direct class
    test_direct_analyzer()
    
    print("\n🎉 Tests completed!")
    print("\n💡 Key improvements:")
    print("- Better error messages for 404 and invalid URLs")
    print("- Proper HTTP status codes (400 for client errors, 500 for server errors)")
    print("- URL validation before attempting download")
    print("- Support for both yt-dlp and direct video file downloads")

if __name__ == "__main__":
    main() 