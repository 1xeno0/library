#!/usr/bin/env python3
"""
Patchwork Clips Analyzer
A comprehensive tool to fetch clips from Patchwork API and analyze them using the Video Analysis API

Features:
- Fetch clips from Patchwork API (all clips or by streamer)
- Send clips to Video Analysis API for AI analysis
- Detailed logging and progress tracking
- Multiple processing modes (mock, real data, all clips)
- Results saving and summary reporting

Usage:
    python3 patchwork_clips_analyzer.py --all-clips --streamers=5 --clips=10
    python3 patchwork_clips_analyzer.py --mock --streamers=3 --clips=5
    python3 patchwork_clips_analyzer.py --help
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

class PatchworkClipsAnalyzer:
    def __init__(self, patchwork_api_key, analysis_api_url="http://localhost:5050"):
        """
        Initialize the Patchwork Clips Analyzer
        
        Args:
            patchwork_api_key (str): API key for Patchwork API
            analysis_api_url (str): URL of the video analysis API
        """
        self.patchwork_api_key = patchwork_api_key
        self.patchwork_base_url = "https://patchwork.gobbo.gg"
        self.analysis_api_url = analysis_api_url
        
        self.patchwork_headers = {
            "x-api-key": patchwork_api_key,
            "Content-Type": "application/json",
            "User-Agent": "PatchworkClipsAnalyzer/1.0"
        }
        
        self.analysis_headers = {
            "Content-Type": "application/json"
        }
        
        self.processed_clips = []
        self.failed_clips = []
        
        print(f"🔧 Initialized Patchwork Clips Analyzer:")
        print(f"   Patchwork API: {self.patchwork_base_url}")
        print(f"   Analysis API: {self.analysis_api_url}")
        print(f"   API Key: {patchwork_api_key[:10]}...{patchwork_api_key[-4:]}")
    
    # ==================== PATCHWORK API METHODS ====================
    
    def get_all_streams(self):
        """Fetch all available streams from Patchwork API"""
        try:
            url = f"{self.patchwork_base_url}/streams"
            print(f"🔍 Fetching streams from: {url}")
            
            response = requests.get(url, headers=self.patchwork_headers, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                streams = response.json()
                print(f"✅ Found {len(streams)} streams")
                
                # Log first few streams for debugging
                print(f"📊 Sample streams:")
                for i, stream in enumerate(streams[:3]):
                    username = stream.get('username', 'Unknown')
                    stream_type = stream.get('type', 'Unknown')
                    print(f"   {i+1}. {username} ({stream_type})")
                
                if len(streams) > 3:
                    print(f"   ... and {len(streams) - 3} more streams")
                
                return streams
            else:
                print(f"❌ Failed to fetch streams: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching streams: {str(e)}")
            return None
    
    def get_all_clips(self, limit=50):
        """Fetch all available clips from Patchwork API"""
        try:
            url = f"{self.patchwork_base_url}/clips"
            print(f"🔍 Fetching all clips from: {url}")
            
            response = requests.get(url, headers=self.patchwork_headers, timeout=30)
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                clips_response = response.json()
                
                if isinstance(clips_response, dict) and 'data' in clips_response:
                    clips = clips_response['data']
                    pages = clips_response.get('pages', 0)
                    print(f"✅ Found {len(clips)} clips across {pages} pages")
                    
                    # Limit to requested number
                    limited_clips = clips[:limit]
                    print(f"✂️  Limited to {len(limited_clips)} clips for processing")
                    
                    return limited_clips
                else:
                    print(f"❌ Unexpected response structure: {clips_response}")
                    return []
            else:
                print(f"❌ Failed to fetch all clips: {response.status_code}")
                print(f"   Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching all clips: {str(e)}")
            return []
    
    def get_clips_for_stream(self, stream_id, limit=10):
        """Fetch clips for a specific stream"""
        try:
            url = f"{self.patchwork_base_url}/clips/stream/{stream_id}"
            print(f"  📹 Fetching clips for stream {stream_id}...")
            
            response = requests.get(url, headers=self.patchwork_headers, timeout=30)
            print(f"  📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                clips_response = response.json()
                
                # Handle the correct API response structure
                if isinstance(clips_response, dict) and 'data' in clips_response:
                    clips = clips_response['data']
                    pages = clips_response.get('pages', 0)
                    print(f"  📊 Found {len(clips)} clips across {pages} pages")
                    
                    # Limit to requested number of clips
                    limited_clips = clips[:limit]
                    print(f"  ✂️  Limited to {len(limited_clips)} clips")
                    
                    return limited_clips
                elif isinstance(clips_response, list):
                    # Fallback for direct array response
                    clips = clips_response
                    print(f"  📊 Found {len(clips)} clips (direct array)")
                    limited_clips = clips[:limit]
                    return limited_clips
                else:
                    print(f"  📊 No clips found for this stream")
                    return []
            else:
                print(f"  ❌ Failed to fetch clips: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ❌ Error fetching clips: {str(e)}")
            return []
    
    # ==================== VIDEO ANALYSIS METHODS ====================
    
    def extract_video_url(self, clip_data):
        """Extract video URL from clip data"""
        print(f"    🔍 Extracting video URL...")
        
        # Try different possible fields for video URL - 'path' is the main field for Patchwork
        url_fields = ['path', 'video_url', 'url', 'link', 'video_link', 'stream_url', 'clip_url']
        
        for field in url_fields:
            if field in clip_data and clip_data[field]:
                print(f"       Found URL in field '{field}': {clip_data[field]}")
                return clip_data[field]
        
        print(f"       No video URL found")
        return None
    
    def send_clip_to_analysis(self, clip_data):
        """Send a clip to the video analysis API with streamer information"""
        try:
            # Extract video URL from clip data
            video_url = self.extract_video_url(clip_data)
            if not video_url:
                print(f"  ⚠️  No video URL found in clip: {clip_data.get('_id', 'unknown')}")
                return None
            
            # Extract streamer information
            streamer_name = clip_data.get('username', '')
            
            # Prepare request for analysis API with streamer info
            analysis_request = {
                "video_link": video_url,
                "streamer_name": streamer_name
            }
            
            clip_title = clip_data.get('title', 'Unknown')
            clip_id = clip_data.get('_id', 'unknown')
            
            print(f"  🔄 Analyzing clip: {clip_title}")
            print(f"     Streamer: {streamer_name}")
            print(f"     Video URL: {video_url}")
            print(f"     Clip ID: {clip_id}")
            
            # Send to analysis API
            url = f"{self.analysis_api_url}/analyse"
            response = requests.post(
                url, 
                json=analysis_request, 
                headers=self.analysis_headers,
                timeout=120  # Longer timeout for video analysis
            )
            
            print(f"     Analysis response status: {response.status_code}")
            
            if response.status_code == 200:
                analysis_result = response.json()
                print(f"  ✅ Analysis completed for clip: {clip_title}")
                print(f"     Detected streamer: {analysis_result.get('streamer', 'Unknown')}")
                print(f"     Game: {analysis_result.get('game', 'Unknown')}")
                print(f"     Platform: {analysis_result.get('platform', 'Unknown')}")
                print(f"     Content type: {analysis_result.get('content_type', 'Unknown')}")
                print(f"     Transcript included: {analysis_result.get('transcript_included', False)}")
                
                # Combine original clip data with analysis
                combined_result = {
                    "original_clip": clip_data,
                    "analysis": analysis_result,
                    "processed_at": datetime.now().isoformat()
                }
                
                return combined_result
            else:
                print(f"  ❌ Analysis failed: {response.status_code}")
                print(f"      Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"  ❌ Error analyzing clip: {str(e)}")
            return None
    
    # ==================== DATA PROCESSING METHODS ====================
    
    def group_clips_by_streamer(self, clips):
        """Group clips by streamer for better organization"""
        print(f"📊 Grouping {len(clips)} clips by streamer...")
        
        streamers_dict = {}
        
        for clip in clips:
            # Extract streamer info from clip
            username = clip.get('username', 'Unknown')
            stream_info = clip.get('stream', {})
            
            if username not in streamers_dict:
                streamers_dict[username] = {
                    "stream": {
                        "username": username,
                        "_id": stream_info.get('_id', 'unknown'),
                        "type": stream_info.get('type', 'unknown')
                    },
                    "clips": []
                }
            
            streamers_dict[username]["clips"].append(clip)
        
        # Convert to list format
        streams_and_clips = list(streamers_dict.values())
        
        print(f"📊 Grouped clips into {len(streams_and_clips)} streamers:")
        for stream_data in streams_and_clips:
            stream_name = stream_data["stream"]["username"]
            clip_count = len(stream_data["clips"])
            print(f"   {stream_name}: {clip_count} clips")
        
        return streams_and_clips
    
    def generate_mock_clips(self, stream_count=5, clips_per_stream=10):
        """Generate mock clips for testing"""
        print("🎭 Generating mock clips for testing...")
        
        mock_streams_and_clips = []
        
        for i in range(stream_count):
            stream_id = f"mock_stream_{i+1}"
            stream_name = f"TestStreamer{i+1}"
            
            clips = []
            for j in range(clips_per_stream):
                clip = {
                    "_id": f"mock_clip_{i+1}_{j+1}",
                    "title": f"Amazing Moment #{j+1} from {stream_name}",
                    "username": stream_name,
                    "path": f"https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Test URL
                    "duration": 30 + (j * 5),
                    "createdDate": f"2025-01-{20+i}T{10+j}:00:00Z"
                }
                clips.append(clip)
            
            mock_streams_and_clips.append({
                "stream": {
                    "_id": stream_id,
                    "username": stream_name,
                    "type": "youtube" if i % 2 == 0 else "twitch"
                },
                "clips": clips
            })
        
        print(f"🎭 Generated {len(mock_streams_and_clips)} mock streamers with {clips_per_stream} clips each")
        return mock_streams_and_clips
    
    # ==================== MAIN PROCESSING METHOD ====================
    
    def process_clips(self, target_streamers=5, clips_per_streamer=10, use_mock=False, use_all_clips=False):
        """
        Main method to process streamers and their clips
        
        Args:
            target_streamers (int): Number of streamers to process
            clips_per_streamer (int): Number of clips per streamer
            use_mock (bool): Use mock data instead of real API
            use_all_clips (bool): Process clips from all available clips instead of by streamer
        """
        print("🚀 Starting Patchwork Clips Analysis...")
        
        if use_all_clips:
            print(f"🎯 Target: Process clips from all available clips (limit: {target_streamers * clips_per_streamer})")
        else:
            print(f"🎯 Target: {target_streamers} streamers, {clips_per_streamer} clips each")
        print("-" * 60)
        
        # Get clips data based on mode
        if use_mock:
            print("🎭 Using mock data mode")
            streams_and_clips = self.generate_mock_clips(target_streamers, clips_per_streamer)
        elif use_all_clips:
            print("📡 Fetching clips from all available clips...")
            all_clips = self.get_all_clips(limit=target_streamers * clips_per_streamer)
            
            if not all_clips:
                print("❌ Could not fetch clips. Try using --mock mode.")
                return None
            
            # Group clips by streamer for better organization
            streams_and_clips = self.group_clips_by_streamer(all_clips)
        else:
            print("📡 Fetching clips by streamer...")
            streams = self.get_all_streams()
            if not streams:
                print("❌ Could not fetch streams. Try using --mock mode or --all-clips mode.")
                return None
            
            # Process selected streamers
            selected_streams = streams[:target_streamers]
            print(f"📺 Selected {len(selected_streams)} streamers:")
            
            for i, stream in enumerate(selected_streams):
                print(f"   {i+1}. {stream.get('username', 'Unknown')} (ID: {stream.get('_id', 'None')})")
            
            streams_and_clips = []
            for stream in selected_streams:
                stream_id = stream.get('_id')
                stream_name = stream.get('username', 'Unknown')
                
                print(f"\n🎬 Processing streamer: {stream_name}")
                
                if not stream_id:
                    print(f"   ⚠️  No valid stream ID found, skipping...")
                    continue
                
                clips = self.get_clips_for_stream(stream_id, clips_per_streamer)
                
                streams_and_clips.append({
                    "stream": stream,
                    "clips": clips
                })
                
                print(f"   ✅ Added {len(clips)} clips for {stream_name}")
                time.sleep(1)  # Rate limiting
        
        # Process clips through analysis API
        print(f"\n🔬 Starting analysis of clips...")
        print("-" * 40)
        
        total_clips = 0
        successful_analyses = 0
        
        for stream_data in streams_and_clips:
            stream = stream_data["stream"]
            clips = stream_data["clips"]
            stream_name = stream.get('username', 'Unknown')
            
            print(f"\n📊 Analyzing clips for {stream_name}:")
            print(f"   Found {len(clips)} clips to analyze")
            
            for i, clip in enumerate(clips):
                total_clips += 1
                print(f"\n   🎬 Processing clip {i+1}/{len(clips)}:")
                
                # Send clip to analysis
                result = self.send_clip_to_analysis(clip)
                
                if result:
                    self.processed_clips.append(result)
                    successful_analyses += 1
                    print(f"   ✅ Successfully analyzed clip {i+1}")
                else:
                    self.failed_clips.append({
                        "clip": clip,
                        "stream": stream_name,
                        "failed_at": datetime.now().isoformat()
                    })
                    print(f"   ❌ Failed to analyze clip {i+1}")
                
                # Delay between analyses
                print(f"   ⏳ Waiting 2 seconds before next analysis...")
                time.sleep(2)
        
        # Generate summary
        summary = {
            "total_streamers": len(streams_and_clips),
            "total_clips": total_clips,
            "successful_analyses": successful_analyses,
            "failed_analyses": len(self.failed_clips),
            "success_rate": (successful_analyses/total_clips*100) if total_clips > 0 else 0
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📈 ANALYSIS SUMMARY:")
        print(f"   Total streamers processed: {summary['total_streamers']}")
        print(f"   Total clips found: {summary['total_clips']}")
        print(f"   Successful analyses: {summary['successful_analyses']}")
        print(f"   Failed analyses: {summary['failed_analyses']}")
        print(f"   Success rate: {summary['success_rate']:.1f}%")
        print("=" * 60)
        
        return {
            "processed_clips": self.processed_clips,
            "failed_clips": self.failed_clips,
            "summary": summary
        }
    
    # ==================== UTILITY METHODS ====================
    
    def save_results(self, results, filename_prefix="patchwork_analysis_results"):
        """Save results to JSON file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename_prefix}.json"
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"💾 Results saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            return None

# ==================== MAIN FUNCTION ====================

def main():
    """Main function to run the Patchwork Clips Analyzer"""
    
    # Configuration
    PATCHWORK_API_KEY = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
    ANALYSIS_API_URL = "http://localhost:5050"
    
    # Default parameters
    target_streamers = 5
    clips_per_streamer = 10
    use_mock = False
    use_all_clips = False
    save_results = True
    
    # Parse command line arguments
    for arg in sys.argv[1:]:
        if arg.startswith("--streamers="):
            target_streamers = int(arg.split("=")[1])
        elif arg.startswith("--clips="):
            clips_per_streamer = int(arg.split("=")[1])
        elif arg.startswith("--api-url="):
            ANALYSIS_API_URL = arg.split("=")[1]
        elif arg == "--mock":
            use_mock = True
        elif arg == "--all-clips":
            use_all_clips = True
        elif arg == "--no-save":
            save_results = False
        elif arg == "--help":
            print("Patchwork Clips Analyzer")
            print("=" * 50)
            print("Usage: python3 patchwork_clips_analyzer.py [options]")
            print("\nOptions:")
            print("  --streamers=N     Number of streamers to process (default: 5)")
            print("  --clips=N         Number of clips per streamer (default: 10)")
            print("  --api-url=URL     Analysis API URL (default: http://localhost:5050)")
            print("  --mock            Use mock data instead of Patchwork API")
            print("  --all-clips       Process clips from all available clips")
            print("  --no-save         Don't save results to file")
            print("  --help            Show this help message")
            print("\nExamples:")
            print("  python3 patchwork_clips_analyzer.py --all-clips --streamers=5 --clips=10")
            print("  python3 patchwork_clips_analyzer.py --mock --streamers=3 --clips=5")
            print("  python3 patchwork_clips_analyzer.py --streamers=2 --clips=3")
            return
    
    # Create analyzer instance
    analyzer = PatchworkClipsAnalyzer(PATCHWORK_API_KEY, ANALYSIS_API_URL)
    
    try:
        # Process clips
        results = analyzer.process_clips(
            target_streamers=target_streamers,
            clips_per_streamer=clips_per_streamer,
            use_mock=use_mock,
            use_all_clips=use_all_clips
        )
        
        if not results:
            print("❌ No results to save")
            return
        
        # Save results if requested
        if save_results:
            analyzer.save_results(results)
        
        print("\n✅ Analysis completed successfully!")
        
        if results["summary"]["successful_analyses"] > 0:
            print(f"🎉 Successfully analyzed {results['summary']['successful_analyses']} clips!")
        
        if results["summary"]["failed_analyses"] > 0:
            print(f"⚠️  {results['summary']['failed_analyses']} clips failed analysis")
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis error: {str(e)}")

if __name__ == "__main__":
    main() 