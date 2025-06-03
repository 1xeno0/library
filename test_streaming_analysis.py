#!/usr/bin/env python3
"""
Test script for enhanced streaming analysis functionality
Tests transcript extraction, streamer detection, and streaming-focused analysis
"""

import sys
import os
import time
import json

# Add the video analysis system to path
sys.path.append('video_analysis_system')
sys.path.append('patchwork_system')

def test_video_analysis_api():
    """Test the video analysis API directly"""
    print("🧪 Testing Video Analysis API...")
    
    try:
        from analyse import VideoAnalyzer
        
        analyzer = VideoAnalyzer()
        
        # Get a real video URL from Patchwork API first
        print("🔍 Getting real video URL from Patchwork API...")
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        patchwork_analyzer = PatchworkClipsAnalyzer("gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs")
        clips = patchwork_analyzer.get_all_clips(limit=1)
        
        if not clips:
            print("⚠️  No clips available from Patchwork API, using mock URL")
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Fallback
            test_streamer = "TestStreamer"
        else:
            clip = clips[0]
            test_url = clip.get('path', '')
            test_streamer = clip.get('username', 'Unknown')
            
            print(f"✅ Found real clip:")
            print(f"   Title: {clip.get('title', 'N/A')}")
            print(f"   Streamer: {test_streamer}")
            print(f"   Duration: {clip.get('duration', 'N/A')} seconds")
        
        print(f"🎬 Testing analysis with:")
        print(f"   URL: {test_url}")
        print(f"   Streamer: {test_streamer}")
        
        result = analyzer.analyze_video(test_url, test_streamer)
        
        print("\n✅ Analysis completed! Results:")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Streamer: {result.get('streamer', 'N/A')}")
        print(f"   Game: {result.get('game', 'N/A')}")
        print(f"   Platform: {result.get('platform', 'N/A')}")
        print(f"   Content Type: {result.get('content_type', 'N/A')}")
        print(f"   Transcript Included: {result.get('transcript_included', False)}")
        print(f"   Transcript Length: {result.get('transcript_length', 0)} characters")
        print(f"   Frames Analyzed: {result.get('frames_analyzed', 0)}")
        print(f"   Tags: {', '.join(result.get('tags', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Video analysis test failed: {str(e)}")
        return False

def test_patchwork_pipeline():
    """Test the Patchwork pipeline with enhanced analysis"""
    print("\n🧪 Testing Patchwork Pipeline...")
    
    try:
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        # Initialize with correct API key
        api_key = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
        analyzer = PatchworkClipsAnalyzer(api_key, "http://localhost:5050")
        
        print("📡 Testing Patchwork API connection...")
        
        # Test getting streams
        streams = analyzer.get_all_streams()
        if streams:
            print(f"✅ Found {len(streams)} streams")
            for i, stream in enumerate(streams[:3]):
                print(f"   {i+1}. {stream.get('username', 'Unknown')}")
        else:
            print("⚠️  No streams found")
        
        # Test getting all clips
        clips = analyzer.get_all_clips(limit=5)
        if clips:
            print(f"✅ Found {len(clips)} clips")
            for i, clip in enumerate(clips[:3]):
                print(f"   {i+1}. {clip.get('title', 'Unknown')} by {clip.get('username', 'Unknown')}")
        else:
            print("⚠️  No clips found")
        
        return True
        
    except Exception as e:
        print(f"❌ Patchwork pipeline test failed: {str(e)}")
        return False

def test_api_endpoint():
    """Test the Flask API endpoint"""
    print("\n🧪 Testing Flask API Endpoint...")
    
    try:
        import requests
        
        # Get a real video URL from Patchwork API first
        print("🔍 Getting real video URL from Patchwork API...")
        from patchwork_clips_analyzer import PatchworkClipsAnalyzer
        
        patchwork_analyzer = PatchworkClipsAnalyzer("gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs")
        clips = patchwork_analyzer.get_all_clips(limit=1)
        
        if not clips:
            print("⚠️  No clips available from Patchwork API, using mock URL")
            test_data = {
                "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "streamer_name": "TestStreamer"
            }
        else:
            clip = clips[0]
            test_data = {
                "video_link": clip.get('path', ''),
                "streamer_name": clip.get('username', 'Unknown')
            }
            print(f"✅ Using real clip from {test_data['streamer_name']}")
        
        print(f"📡 Sending request to http://localhost:5050/analyse")
        print(f"   Data: {test_data}")
        
        response = requests.post(
            "http://localhost:5050/analyse",
            json=test_data,
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API endpoint working! Response:")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Streamer: {result.get('streamer', 'N/A')}")
            print(f"   Game: {result.get('game', 'N/A')}")
            print(f"   Platform: {result.get('platform', 'N/A')}")
            print(f"   Transcript Included: {result.get('transcript_included', False)}")
            return True
        else:
            print(f"❌ API returned error: {response.text}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running. Start it with: cd video_analysis_system && python app.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Streaming Analysis Tests")
    print("=" * 60)
    
    # Check environment variables
    print("🔧 Checking environment...")
    openai_key = os.getenv('OPENAI_API_KEY')
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not openai_key:
        print("⚠️  OPENAI_API_KEY not set")
    else:
        print(f"✅ OpenAI API key configured (length: {len(openai_key)})")
    
    if not mongodb_uri:
        print("⚠️  MONGODB_URI not set")
    else:
        print("✅ MongoDB URI configured")
    
    print()
    
    # Run tests
    tests = [
        ("Video Analysis API", test_video_analysis_api),
        ("Patchwork Pipeline", test_patchwork_pipeline),
        ("Flask API Endpoint", test_api_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(1)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The enhanced streaming analysis is ready!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("\n📝 Next steps:")
    print("1. Start the video analysis API: cd video_analysis_system && python app.py")
    print("2. Run Patchwork analysis: cd patchwork_system && python3 patchwork_clips_analyzer.py --all-clips --streamers=2 --clips=3")
    print("3. Search for clips: curl 'http://localhost:5050/find_clips' -X POST -H 'Content-Type: application/json' -d '{\"search_query\":\"gaming\"}'")

if __name__ == "__main__":
    main() 