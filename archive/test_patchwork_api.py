#!/usr/bin/env python3
"""
Simple test script to check Patchwork API endpoints and authentication methods
"""

import requests
import json

def test_endpoint(url, headers=None, description=""):
    """Test a single endpoint with given headers"""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    print(f"   Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Success! Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"   📊 Items count: {len(data)}")
                elif isinstance(data, dict):
                    print(f"   📊 Keys: {list(data.keys())}")
                return True
            except:
                print(f"   ✅ Success! Response length: {len(response.text)}")
                return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    base_url = "https://patchwork.gobbo.gg"
    api_key = "Ab3dE5Fg7Hi9Jk1Lm3NoPq-StUvWxYz0123456789AB"
    
    print("🚀 Testing Patchwork API endpoints...")
    print("=" * 50)
    
    # Test different authentication methods
    auth_methods = [
        (None, "No authentication"),
        ({"x-api-key": api_key}, "x-api-key header"),
        ({"Authorization": f"Bearer {api_key}"}, "Bearer token"),
        ({"Authorization": f"Api-Key {api_key}"}, "Api-Key authorization"),
        ({"api-key": api_key}, "api-key header (lowercase)"),
        ({"X-API-KEY": api_key}, "X-API-KEY header (uppercase)"),
    ]
    
    endpoints = [
        "/clips",
        "/streams"
    ]
    
    for endpoint in endpoints:
        print(f"\n{'='*20} TESTING {endpoint} {'='*20}")
        
        for headers, auth_desc in auth_methods:
            url = f"{base_url}{endpoint}"
            test_endpoint(url, headers, f"{endpoint} with {auth_desc}")
    
    # Test specific stream clips endpoint if we know a stream ID
    print(f"\n{'='*20} TESTING STREAM-SPECIFIC CLIPS {'='*20}")
    
    # Try with a sample stream ID from the API spec
    sample_stream_id = "678ef66b9083a4518f3030a6"
    
    for headers, auth_desc in auth_methods:
        url = f"{base_url}/clips/stream/{sample_stream_id}"
        test_endpoint(url, headers, f"Stream clips with {auth_desc}")

if __name__ == "__main__":
    main() 