#!/usr/bin/env python3
"""
Script to fetch clips from Patchwork API and analyze them using the local analysis API
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
PATCHWORK_API_KEY = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
PATCHWORK_BASE_URL = "https://patchwork.gobbo.gg"
LOCAL_API_BASE_URL = "http://localhost:5050"

# Headers for Patchwork API
patchwork_headers = {
    "x-api-key": PATCHWORK_API_KEY
}

def check_local_api():
    """Check if local analysis API is running"""
    try:
        response = requests.get(f"{LOCAL_API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Local analysis API is running")
            return True
        else:
            print(f"❌ Local analysis API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Local analysis API is not accessible: {e}")
        print("Please start the analysis API first: python3 app.py")
        return False

def fetch_clips_from_patchwork(limit=50):
    """Fetch clips from Patchwork API"""
    print(f"🔍 Fetching {limit} clips from Patchwork API...")
    
    try:
        response = requests.get(
            f"{PATCHWORK_BASE_URL}/clips",
            headers=patchwork_headers,
            params={"limit": limit},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch clips: {response.status_code}")
            print(f"Response: {response.text}")
            return []
        
        clips = response.json()
        print(f"✅ Successfully fetched {len(clips)} clips")
        return clips
        
    except Exception as e:
        print(f"❌ Error fetching clips: {e}")
        return []

def get_video_url_from_clip(clip):
    """Extract video URL from clip data"""
    # Try different possible fields for video URL
    possible_fields = ['videoUrl', 'url', 'video_url', 'downloadUrl', 'streamUrl']
    
    for field in possible_fields:
        if field in clip and clip[field]:
            return clip[field]
    
    # If no direct URL, try to construct from clip data
    if 'id' in clip:
        # Try common patterns
        possible_urls = [
            f"https://patchwork.gobbo.gg/clips/{clip['id']}/video",
            f"https://patchwork.gobbo.gg/api/clips/{clip['id']}/download"
        ]
        return possible_urls[0]  # Return first attempt
    
    return None

def analyze_video_with_local_api(video_url):
    """Analyze video using local analysis API"""
    try:
        payload = {"video_link": video_url}
        
        response = requests.post(
            f"{LOCAL_API_BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300  # 5 minutes timeout for analysis
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Analysis failed for {video_url}: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing video {video_url}: {e}")
        return None

def process_clips(clips, max_to_process=50):
    """Process clips through the analysis pipeline"""
    print(f"\n🔄 Processing {min(len(clips), max_to_process)} clips...")
    
    successful_analyses = 0
    failed_analyses = 0
    
    for i, clip in enumerate(clips[:max_to_process]):
        print(f"\n📹 Processing clip {i+1}/{min(len(clips), max_to_process)}")
        
        # Extract video URL
        video_url = get_video_url_from_clip(clip)
        if not video_url:
            print(f"❌ No video URL found for clip: {clip.get('id', 'unknown')}")
            failed_analyses += 1
            continue
        
        print(f"🔗 Video URL: {video_url}")
        
        # Analyze video
        print("🤖 Analyzing video content...")
        analysis_result = analyze_video_with_local_api(video_url)
        
        if analysis_result:
            print(f"✅ Analysis successful!")
            print(f"   Title: {analysis_result.get('title', 'N/A')}")
            print(f"   Tags: {analysis_result.get('tags', [])}")
            successful_analyses += 1
        else:
            print(f"❌ Analysis failed")
            failed_analyses += 1
        
        # Add delay to avoid overwhelming the APIs
        if i < len(clips) - 1:
            print("⏳ Waiting 2 seconds before next analysis...")
            time.sleep(2)
    
    print(f"\n📊 Processing Summary:")
    print(f"   ✅ Successful analyses: {successful_analyses}")
    print(f"   ❌ Failed analyses: {failed_analyses}")
    print(f"   📈 Success rate: {(successful_analyses/(successful_analyses+failed_analyses)*100):.1f}%")
    
    return successful_analyses, failed_analyses

def main():
    """Main function"""
    print("=" * 60)
    print("🎬 PATCHWORK CLIPS ANALYZER")
    print("=" * 60)
    
    # Check if local API is running
    if not check_local_api():
        return False
    
    # Ask user how many clips to process
    try:
        num_clips = input("\nHow many clips would you like to analyze? (default: 50): ").strip()
        if not num_clips:
            num_clips = 50
        else:
            num_clips = int(num_clips)
            
        if num_clips <= 0:
            print("❌ Number of clips must be positive")
            return False
            
    except ValueError:
        print("❌ Invalid number entered")
        return False
    
    # Fetch clips from Patchwork API
    clips = fetch_clips_from_patchwork(limit=num_clips)
    if not clips:
        print("❌ No clips fetched, exiting")
        return False
    
    # Show sample clip data
    print(f"\n📋 Sample clip data:")
    sample_clip = clips[0]
    print(json.dumps(sample_clip, indent=2)[:500] + "..." if len(json.dumps(sample_clip, indent=2)) > 500 else json.dumps(sample_clip, indent=2))
    
    # Ask for confirmation
    confirm = input(f"\nProceed with analyzing {len(clips)} clips? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Analysis cancelled by user")
        return False
    
    # Process clips
    successful, failed = process_clips(clips, max_to_process=num_clips)
    
    if successful > 0:
        print(f"\n🎉 Successfully analyzed {successful} videos!")
        print("You can now use the search functionality in the web interface.")
    else:
        print("\n😞 No videos were successfully analyzed.")
    
    return successful > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 