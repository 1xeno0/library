#!/usr/bin/env python3
"""
Comprehensive test runner for the Patchwork Library Analyzer + Search API
Runs both video analysis and search functionality tests
"""

import sys
import os
import subprocess
import time
import requests

def check_server_status():
    """Check if the API server is running"""
    try:
        response = requests.get("http://localhost:5050/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_server_if_needed():
    """Start the server if it's not running"""
    if check_server_status():
        print("✅ Server is already running")
        return True
    
    print("🚀 Starting server...")
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "start.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_server_status():
                print("✅ Server started successfully")
                return True
            print(f"⏳ Waiting for server... ({i+1}/30)")
        
        print("❌ Server failed to start within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def run_test_file(test_file, description):
    """Run a specific test file"""
    print("\n" + "=" * 80)
    print(f"🧪 RUNNING {description}")
    print("=" * 80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        return False

def main():
    """Main test runner"""
    print("=" * 80)
    print("🧪 PATCHWORK LIBRARY - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This will run all tests for video analysis and search functionality")
    print()
    
    # Check if test files exist
    test_files = [
        ("test_video_analysis.py", "VIDEO ANALYSIS TESTS"),
        ("test_video_search.py", "VIDEO SEARCH TESTS")
    ]
    
    missing_files = []
    for test_file, _ in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    # Check server status
    print("🔍 Checking server status...")
    if not check_server_status():
        print("⚠️  Server is not running")
        start_choice = input("Start server automatically? (y/n): ").lower()
        
        if start_choice == 'y':
            if not start_server_if_needed():
                print("❌ Cannot run tests without server")
                return False
        else:
            print("❌ Please start the server manually: python3 start.py")
            return False
    else:
        print("✅ Server is running")
    
    # Ask about test preferences
    print("\n" + "=" * 80)
    print("🎛️  TEST CONFIGURATION")
    print("=" * 80)
    
    print("Test options:")
    print("1. Quick tests only (validation, mocking, basic functionality)")
    print("2. Full tests (includes expensive API calls and database operations)")
    print("3. Custom selection")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    if choice == "3":
        print("\nCustom test selection:")
        run_analysis = input("Run video analysis tests? (y/n): ").lower() == 'y'
        run_search = input("Run video search tests? (y/n): ").lower() == 'y'
        
        if not run_analysis and not run_search:
            print("❌ No tests selected")
            return False
            
        selected_tests = []
        if run_analysis:
            selected_tests.append(("test_video_analysis.py", "VIDEO ANALYSIS TESTS"))
        if run_search:
            selected_tests.append(("test_video_search.py", "VIDEO SEARCH TESTS"))
    else:
        # Run all tests
        selected_tests = test_files
    
    # Set environment variable for test mode
    if choice == "1":
        os.environ["TEST_MODE"] = "quick"
        print("🏃 Running in QUICK mode (no expensive operations)")
    else:
        os.environ["TEST_MODE"] = "full"
        print("🐌 Running in FULL mode (includes expensive operations)")
    
    # Run selected tests
    results = {}
    total_passed = 0
    total_failed = 0
    
    for test_file, description in selected_tests:
        print(f"\n⏳ Starting {description}...")
        success = run_test_file(test_file, description)
        results[description] = success
        
        if success:
            total_passed += 1
            print(f"✅ {description} - PASSED")
        else:
            total_failed += 1
            print(f"❌ {description} - FAILED")
    
    # Print final summary
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    for description, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description}: {status}")
    
    print(f"\nSummary: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("Your Patchwork Library system is working correctly!")
    else:
        print(f"\n⚠️  {total_failed} test suite(s) failed")
        print("Check the output above for details on what went wrong.")
    
    # Cleanup
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]
    
    return total_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 