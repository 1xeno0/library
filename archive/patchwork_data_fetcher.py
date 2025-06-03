#!/usr/bin/env python3
"""
Patchwork API Data Fetcher
Fetches recent streams and clips data from the Patchwork API
"""

import requests
import json
from datetime import datetime, timedelta
import time
import sys

class PatchworkDataFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://patchwork.gobbo.gg"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "PatchworkDataFetcher/1.0"
        }
        
    def test_api_connection(self):
        """Test API connection and authentication"""
        print("🔍 Testing API connection and authentication...")
        
        # Try different endpoints to test auth
        test_endpoints = [
            ("/clips", "GET", "Public clips endpoint"),
            ("/streams", "GET", "Streams endpoint (requires auth)")
        ]
        
        for endpoint, method, description in test_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                print(f"   Testing {description}: {method} {endpoint}")
                
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    print(f"   ✅ Success: {response.status_code}")
                    return True
                elif response.status_code == 401:
                    print(f"   ❌ Unauthorized: {response.status_code} - {response.text}")
                elif response.status_code == 403:
                    print(f"   ❌ Forbidden: {response.status_code} - {response.text}")
                else:
                    print(f"   ⚠️  Unexpected status: {response.status_code} - {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Connection error: {str(e)}")
        
        return False
        
    def get_streams(self):
        """Fetch all streams"""
        try:
            url = f"{self.base_url}/streams"
            print(f"   Making request to: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully fetched {len(data) if isinstance(data, list) else 'streams'} streams")
                return data
            else:
                print(f"❌ Failed to fetch streams: {response.status_code}")
                print(f"   Response body: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching streams: {str(e)}")
            return None
    
    def get_clips(self):
        """Fetch all clips"""
        try:
            url = f"{self.base_url}/clips"
            print(f"   Making request to: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully fetched {len(data) if isinstance(data, list) else 'clips'} clips")
                return data
            else:
                print(f"❌ Failed to fetch clips: {response.status_code}")
                print(f"   Response body: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching clips: {str(e)}")
            return None
    
    def get_clips_by_stream(self, stream_id):
        """Fetch clips for a specific stream"""
        try:
            url = f"{self.base_url}/clips/stream/{stream_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Successfully fetched clips for stream {stream_id}")
                return data
            else:
                print(f"❌ Failed to fetch clips for stream {stream_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching clips for stream {stream_id}: {str(e)}")
            return None
    
    def generate_mock_data(self):
        """Generate mock data for testing when API is not accessible"""
        print("🎭 Generating mock data for testing...")
        
        mock_streams = [
            {
                "id": "mock_stream_1",
                "username": "TestStreamer1",
                "type": "youtube",
                "created_at": "2025-01-20T10:00:00Z"
            },
            {
                "id": "mock_stream_2", 
                "username": "TestStreamer2",
                "type": "twitch",
                "created_at": "2025-01-21T15:30:00Z"
            }
        ]
        
        mock_clips = [
            {
                "id": "mock_clip_1",
                "title": "Amazing Gaming Moment",
                "stream_id": "mock_stream_1",
                "created_at": "2025-01-20T10:15:00Z",
                "duration": 30
            },
            {
                "id": "mock_clip_2",
                "title": "Epic Fail Compilation",
                "stream_id": "mock_stream_2", 
                "created_at": "2025-01-21T16:00:00Z",
                "duration": 45
            }
        ]
        
        return {
            "fetch_timestamp": datetime.now().isoformat(),
            "streams": mock_streams,
            "clips": mock_clips,
            "clips_by_stream": {
                "mock_stream_1": [mock_clips[0]],
                "mock_stream_2": [mock_clips[1]]
            },
            "mock_data": True
        }
    
    def save_data_to_file(self, data, filename):
        """Save data to JSON file with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_with_timestamp = f"{timestamp}_{filename}"
            
            with open(filename_with_timestamp, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"💾 Data saved to {filename_with_timestamp}")
            return filename_with_timestamp
            
        except Exception as e:
            print(f"❌ Error saving data to file: {str(e)}")
            return None
    
    def fetch_all_recent_data(self, save_to_files=True, test_connection=True, use_mock=False):
        """Fetch all recent data from the API"""
        print("🚀 Starting Patchwork API data fetch...")
        print(f"📡 API Base URL: {self.base_url}")
        print(f"🔑 Using API Key: {self.api_key[:10]}...")
        print("-" * 50)
        
        # If mock mode is requested, return mock data
        if use_mock:
            print("🎭 Using mock data mode")
            mock_data = self.generate_mock_data()
            if save_to_files:
                self.save_data_to_file(mock_data, "patchwork_mock_data.json")
            return mock_data
        
        # Test connection first if requested
        connection_ok = True
        if test_connection:
            connection_ok = self.test_api_connection()
            if not connection_ok:
                print("\n⚠️  API connection test failed.")
                print("🔧 This could mean:")
                print("   - Your API key is invalid or expired")
                print("   - The API endpoints have changed")
                print("   - Network connectivity issues")
                print("   - API server is down")
                print("\n💡 Try running with --mock to test with sample data")
                print("💡 Or check your API key with the Patchwork team")
        
        all_data = {
            "fetch_timestamp": datetime.now().isoformat(),
            "streams": None,
            "clips": None,
            "clips_by_stream": {}
        }
        
        # Fetch streams
        print("\n📺 Fetching streams...")
        streams = self.get_streams()
        all_data["streams"] = streams
        
        if save_to_files and streams:
            self.save_data_to_file(streams, "patchwork_streams.json")
        
        # Fetch all clips
        print("\n🎬 Fetching all clips...")
        clips = self.get_clips()
        all_data["clips"] = clips
        
        if save_to_files and clips:
            self.save_data_to_file(clips, "patchwork_clips.json")
        
        # If we have streams, fetch clips for each stream
        if streams and isinstance(streams, list):
            print(f"\n🔍 Fetching clips for each stream...")
            for stream in streams:
                if isinstance(stream, dict) and 'id' in stream:
                    stream_id = stream['id']
                    print(f"  📹 Fetching clips for stream: {stream.get('username', stream_id)}")
                    stream_clips = self.get_clips_by_stream(stream_id)
                    if stream_clips:
                        all_data["clips_by_stream"][stream_id] = stream_clips
                    
                    # Small delay to be respectful to the API
                    time.sleep(0.5)
        
        # Save complete dataset
        if save_to_files:
            print("\n💾 Saving complete dataset...")
            self.save_data_to_file(all_data, "patchwork_complete_data.json")
        
        print("\n" + "=" * 50)
        print("📊 FETCH SUMMARY:")
        print(f"   Streams: {len(streams) if streams and isinstance(streams, list) else 'N/A'}")
        print(f"   All Clips: {len(clips) if clips and isinstance(clips, list) else 'N/A'}")
        print(f"   Streams with clips: {len(all_data['clips_by_stream'])}")
        print("=" * 50)
        
        return all_data
    
    def analyze_recent_activity(self, data):
        """Analyze the fetched data for recent activity"""
        print("\n🔍 ANALYZING RECENT ACTIVITY:")
        print("-" * 30)
        
        if data.get("mock_data"):
            print("📝 Note: This analysis is based on mock data")
        
        # Analyze streams
        if data.get("streams"):
            streams = data["streams"]
            if isinstance(streams, list):
                print(f"📺 Total Streams: {len(streams)}")
                
                # Show stream details
                for i, stream in enumerate(streams[:5]):  # Show first 5
                    if isinstance(stream, dict):
                        username = stream.get('username', 'Unknown')
                        stream_type = stream.get('type', 'Unknown')
                        print(f"   {i+1}. {username} ({stream_type})")
                
                if len(streams) > 5:
                    print(f"   ... and {len(streams) - 5} more streams")
        
        # Analyze clips
        if data.get("clips"):
            clips = data["clips"]
            if isinstance(clips, list):
                print(f"\n🎬 Total Clips: {len(clips)}")
                
                # Try to find recent clips (if timestamp info is available)
                recent_clips = []
                for clip in clips:
                    if isinstance(clip, dict):
                        # Look for timestamp fields
                        for time_field in ['created_at', 'timestamp', 'date', 'createdAt']:
                            if time_field in clip:
                                recent_clips.append(clip)
                                break
                
                if recent_clips:
                    print(f"   Recent clips found: {len(recent_clips)}")
                else:
                    print("   No timestamp information found in clips")
        
        # Analyze clips by stream
        clips_by_stream = data.get("clips_by_stream", {})
        if clips_by_stream:
            print(f"\n📊 Clips by Stream Analysis:")
            for stream_id, stream_clips in clips_by_stream.items():
                if isinstance(stream_clips, list):
                    print(f"   Stream {stream_id}: {len(stream_clips)} clips")

def print_api_key_help():
    """Print help for getting a valid API key"""
    print("\n🔑 HOW TO GET A VALID PATCHWORK API KEY:")
    print("-" * 40)
    print("1. Visit the Patchwork website: https://patchwork.gobbo.gg")
    print("2. Sign up for an account or log in")
    print("3. Navigate to your account settings or developer section")
    print("4. Generate a new API key")
    print("5. Replace the API_KEY variable in this script with your new key")
    print("\n📧 If you need help, contact the Patchwork team")
    print("🔗 Check their documentation for API access requirements")

def main():
    # API configuration
    API_KEY = "gv4Gp1OeZhF5eBNU7vDjDL-yqZ6vrCfdCzF7HGVMiCs"
    
    # Create fetcher instance
    fetcher = PatchworkDataFetcher(API_KEY)
    
    # Check command line arguments
    save_files = True
    debug_mode = False
    use_mock = False
    
    for arg in sys.argv[1:]:
        if arg == "--no-save":
            save_files = False
            print("📝 Running in no-save mode (data won't be saved to files)")
        elif arg == "--debug":
            debug_mode = True
            print("🐛 Debug mode enabled")
        elif arg == "--mock":
            use_mock = True
            print("🎭 Mock data mode enabled")
        elif arg == "--help":
            print("Usage: python patchwork_data_fetcher.py [options]")
            print("Options:")
            print("  --no-save    Don't save data to files")
            print("  --debug      Enable debug mode")
            print("  --mock       Use mock data instead of API")
            print("  --help       Show this help message")
            print_api_key_help()
            return
    
    try:
        # Fetch all data
        data = fetcher.fetch_all_recent_data(
            save_to_files=save_files, 
            test_connection=debug_mode,
            use_mock=use_mock
        )
        
        # Analyze the data
        fetcher.analyze_recent_activity(data)
        
        print("\n✅ Data fetch completed successfully!")
        
        if save_files:
            print("📁 Check the generated JSON files for detailed data")
        
        # If no data was fetched and not using mock, provide troubleshooting tips
        if not use_mock and not data.get("streams") and not data.get("clips"):
            print("\n🔧 TROUBLESHOOTING:")
            print("   - Check if your API key is valid")
            print("   - Verify the API endpoints are accessible")
            print("   - Try running with --debug for more information")
            print("   - Try running with --mock to test with sample data")
            print("   - Check if the API requires different authentication")
            print_api_key_help()
        
    except KeyboardInterrupt:
        print("\n⚠️  Fetch interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main() 