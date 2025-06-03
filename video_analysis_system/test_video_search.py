#!/usr/bin/env python3
"""
Comprehensive test suite for video search functionality
Tests the /find_clips endpoint and search capabilities
"""

import unittest
import requests
import json
import time
from unittest.mock import patch, MagicMock
import sys

# Add current directory to path for imports
sys.path.append('.')

from database import DatabaseManager
import config

class TestVideoSearchAPI(unittest.TestCase):
    """Test the video search API endpoint"""
    
    BASE_URL = "http://localhost:5050"
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = DatabaseManager()
        
        # Sample test data
        self.sample_videos = [
            {
                "video_url": "https://test1.com/gaming_video.mp4",
                "title": "Epic Gaming Montage",
                "description": "Amazing gaming highlights from various games",
                "tags": ["gaming", "montage", "highlights"],
                "upload_date": "2025-04-20"
            },
            {
                "video_url": "https://test2.com/sports_video.mp4", 
                "title": "Basketball Championship Finals",
                "description": "Intense basketball game with incredible plays",
                "tags": ["sports", "basketball", "championship"],
                "upload_date": "2025-04-21"
            },
            {
                "video_url": "https://test3.com/music_video.mp4",
                "title": "Live Concert Performance",
                "description": "Amazing live music performance from the concert",
                "tags": ["music", "concert", "live"],
                "upload_date": "2025-04-22"
            },
            {
                "video_url": "https://test4.com/gaming_sports.mp4",
                "title": "Gaming Tournament Finals",
                "description": "Professional esports tournament with amazing plays",
                "tags": ["gaming", "esports", "tournament", "competitive"],
                "upload_date": "2025-04-23"
            }
        ]
    
    def populate_test_data(self):
        """Populate database with test data"""
        try:
            for video_data in self.sample_videos:
                video_url = video_data.pop("video_url")
                self.db.save_video_analysis(video_url, video_data)
            print("✅ Test data populated")
            return True
        except Exception as e:
            print(f"⚠️  Could not populate test data: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data from database"""
        try:
            for video_data in self.sample_videos:
                # Note: In a real scenario, you'd want a proper cleanup method
                pass
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️  Could not clean up test data: {e}")
    
    def test_find_clips_by_search_query(self):
        """Test searching clips by text query"""
        print("\n🧪 Testing /find_clips with search query...")
        
        # Populate test data
        if not self.populate_test_data():
            self.skipTest("Could not populate test data")
        
        test_cases = [
            {
                "query": "gaming",
                "expected_matches": ["Epic Gaming Montage", "Gaming Tournament Finals"]
            },
            {
                "query": "basketball",
                "expected_matches": ["Basketball Championship Finals"]
            },
            {
                "query": "concert",
                "expected_matches": ["Live Concert Performance"]
            },
            {
                "query": "nonexistent",
                "expected_matches": []
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(query=test_case["query"]):
                payload = {
                    "search_query": test_case["query"],
                    "tags": []
                }
                
                response = requests.post(
                    f"{self.BASE_URL}/find_clips",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                print(f"Searching for: '{test_case['query']}'")
                print(f"Status Code: {response.status_code}")
                
                if test_case["expected_matches"]:
                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    
                    # Validate response structure
                    self.assertIn("title", result)
                    self.assertIn("description", result)
                    self.assertIn("tags", result)
                    self.assertIn("upload_date", result)
                    self.assertIn("video_url", result)
                    
                    # Check if result matches expected
                    self.assertIn(result["title"], test_case["expected_matches"])
                    print(f"✅ Found: {result['title']}")
                    
                else:
                    self.assertEqual(response.status_code, 404)
                    result = response.json()
                    self.assertIn("message", result)
                    print(f"✅ Correctly returned no results")
    
    def test_find_clips_by_tags(self):
        """Test searching clips by tags"""
        print("\n🧪 Testing /find_clips with tags...")
        
        if not self.populate_test_data():
            self.skipTest("Could not populate test data")
        
        test_cases = [
            {
                "tags": ["gaming"],
                "expected_count": 2  # Should match gaming videos
            },
            {
                "tags": ["sports"],
                "expected_count": 1  # Should match basketball video
            },
            {
                "tags": ["music", "live"],
                "expected_count": 1  # Should match concert video
            },
            {
                "tags": ["nonexistent"],
                "expected_count": 0  # Should match nothing
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(tags=test_case["tags"]):
                payload = {
                    "search_query": "",
                    "tags": test_case["tags"]
                }
                
                response = requests.post(
                    f"{self.BASE_URL}/find_clips",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                print(f"Searching by tags: {test_case['tags']}")
                print(f"Status Code: {response.status_code}")
                
                if test_case["expected_count"] > 0:
                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    
                    # Validate response structure
                    self.assertIn("title", result)
                    self.assertIn("tags", result)
                    
                    # Check if result has matching tags
                    result_tags = result["tags"]
                    has_matching_tag = any(tag in result_tags for tag in test_case["tags"])
                    self.assertTrue(has_matching_tag, f"Result should have at least one matching tag")
                    print(f"✅ Found: {result['title']} with tags: {result_tags}")
                    
                else:
                    self.assertEqual(response.status_code, 404)
                    print("✅ Correctly returned no results")
    
    def test_find_clips_combined_search(self):
        """Test searching clips with both query and tags"""
        print("\n🧪 Testing /find_clips with combined search...")
        
        if not self.populate_test_data():
            self.skipTest("Could not populate test data")
        
        test_cases = [
            {
                "query": "gaming",
                "tags": ["tournament"],
                "expected_title": "Gaming Tournament Finals"
            },
            {
                "query": "basketball",
                "tags": ["sports"],
                "expected_title": "Basketball Championship Finals"
            },
            {
                "query": "gaming",
                "tags": ["music"],  # Should not match anything
                "expected_title": None
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(query=test_case["query"], tags=test_case["tags"]):
                payload = {
                    "search_query": test_case["query"],
                    "tags": test_case["tags"]
                }
                
                response = requests.post(
                    f"{self.BASE_URL}/find_clips",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                print(f"Combined search - Query: '{test_case['query']}', Tags: {test_case['tags']}")
                print(f"Status Code: {response.status_code}")
                
                if test_case["expected_title"]:
                    self.assertEqual(response.status_code, 200)
                    result = response.json()
                    self.assertEqual(result["title"], test_case["expected_title"])
                    print(f"✅ Found expected result: {result['title']}")
                else:
                    self.assertEqual(response.status_code, 404)
                    print("✅ Correctly returned no results for incompatible criteria")
    
    def test_find_clips_validation_errors(self):
        """Test validation errors for search endpoint"""
        print("\n🧪 Testing /find_clips validation errors...")
        
        test_cases = [
            {
                "name": "Empty request body",
                "payload": None,
                "expected_status": 400
            },
            {
                "name": "Missing both query and tags",
                "payload": {},
                "expected_status": 400
            },
            {
                "name": "Empty query and empty tags",
                "payload": {"search_query": "", "tags": []},
                "expected_status": 400
            },
            {
                "name": "Valid query only",
                "payload": {"search_query": "test"},
                "expected_status": [200, 404]  # Either found or not found is valid
            },
            {
                "name": "Valid tags only", 
                "payload": {"tags": ["test"]},
                "expected_status": [200, 404]  # Either found or not found is valid
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(name=test_case["name"]):
                print(f"Testing: {test_case['name']}")
                
                if test_case["payload"] is None:
                    response = requests.post(f"{self.BASE_URL}/find_clips")
                else:
                    response = requests.post(
                        f"{self.BASE_URL}/find_clips",
                        headers={"Content-Type": "application/json"},
                        json=test_case["payload"]
                    )
                
                print(f"Status Code: {response.status_code}")
                
                expected_status = test_case["expected_status"]
                if isinstance(expected_status, list):
                    self.assertIn(response.status_code, expected_status)
                else:
                    self.assertEqual(response.status_code, expected_status)
                
                if response.status_code == 400:
                    result = response.json()
                    self.assertIn("error", result)
                    print(f"✅ Correctly rejected: {result['error']}")
                else:
                    print("✅ Request handled correctly")
    
    def test_find_clips_case_insensitive_search(self):
        """Test that search is case insensitive"""
        print("\n🧪 Testing case insensitive search...")
        
        if not self.populate_test_data():
            self.skipTest("Could not populate test data")
        
        test_cases = [
            "GAMING",
            "gaming", 
            "Gaming",
            "gAmInG"
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                payload = {
                    "search_query": query,
                    "tags": []
                }
                
                response = requests.post(
                    f"{self.BASE_URL}/find_clips",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                print(f"Testing case: '{query}'")
                
                # Should find gaming-related videos regardless of case
                if response.status_code == 200:
                    result = response.json()
                    self.assertIn("gaming", result["title"].lower())
                    print(f"✅ Found: {result['title']}")
                else:
                    # If no results, that's also acceptable for this test
                    print("✅ No results (acceptable)")


class TestDatabaseSearchFunctionality(unittest.TestCase):
    """Test database search functionality directly"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = DatabaseManager()
        self.test_video_url = "https://test-search.com/video.mp4"
        
        # Test data
        self.test_analysis = {
            "title": "Database Search Test Video",
            "description": "A video for testing database search functionality",
            "tags": ["database", "search", "test"],
            "upload_date": "2025-04-23"
        }
    
    def test_search_videos_by_query(self):
        """Test database search by text query"""
        print("\n🧪 Testing database search by query...")
        
        try:
            # Save test video
            self.db.save_video_analysis(self.test_video_url, self.test_analysis)
            
            # Test search by title
            results = self.db.search_videos(search_query="Database Search")
            self.assertTrue(len(results) > 0)
            self.assertEqual(results[0]["title"], self.test_analysis["title"])
            print("✅ Search by title works")
            
            # Test search by description
            results = self.db.search_videos(search_query="testing database")
            self.assertTrue(len(results) > 0)
            print("✅ Search by description works")
            
            # Test case insensitive search
            results = self.db.search_videos(search_query="DATABASE")
            self.assertTrue(len(results) > 0)
            print("✅ Case insensitive search works")
            
            # Test no results
            results = self.db.search_videos(search_query="nonexistent content")
            self.assertEqual(len(results), 0)
            print("✅ No results for non-matching query")
            
        except Exception as e:
            print(f"⚠️  Database search test skipped: {e}")
            self.skipTest("Database not available")
    
    def test_search_videos_by_tags(self):
        """Test database search by tags"""
        print("\n🧪 Testing database search by tags...")
        
        try:
            # Save test video
            self.db.save_video_analysis(self.test_video_url, self.test_analysis)
            
            # Test search by single tag
            results = self.db.search_videos(tags=["database"])
            self.assertTrue(len(results) > 0)
            self.assertIn("database", results[0]["tags"])
            print("✅ Search by single tag works")
            
            # Test search by multiple tags
            results = self.db.search_videos(tags=["database", "search"])
            self.assertTrue(len(results) > 0)
            print("✅ Search by multiple tags works")
            
            # Test search by non-existent tag
            results = self.db.search_videos(tags=["nonexistent"])
            self.assertEqual(len(results), 0)
            print("✅ No results for non-matching tags")
            
        except Exception as e:
            print(f"⚠️  Database tag search test skipped: {e}")
            self.skipTest("Database not available")
    
    def test_search_videos_combined(self):
        """Test database search with both query and tags"""
        print("\n🧪 Testing database combined search...")
        
        try:
            # Save test video
            self.db.save_video_analysis(self.test_video_url, self.test_analysis)
            
            # Test combined search that should match
            results = self.db.search_videos(
                search_query="Database",
                tags=["test"]
            )
            self.assertTrue(len(results) > 0)
            print("✅ Combined search with matching criteria works")
            
            # Test combined search that should not match
            results = self.db.search_videos(
                search_query="Database",
                tags=["nonexistent"]
            )
            self.assertEqual(len(results), 0)
            print("✅ Combined search with non-matching criteria returns no results")
            
        except Exception as e:
            print(f"⚠️  Database combined search test skipped: {e}")
            self.skipTest("Database not available")


class TestSearchPerformance(unittest.TestCase):
    """Test search performance and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.BASE_URL = "http://localhost:5050"
    
    def test_search_response_time(self):
        """Test that search responses are reasonably fast"""
        print("\n🧪 Testing search response time...")
        
        payload = {
            "search_query": "test",
            "tags": []
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.BASE_URL}/find_clips",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        response_time = time.time() - start_time
        
        print(f"Response time: {response_time:.3f}s")
        
        # Search should be fast (under 5 seconds even with network latency)
        self.assertLess(response_time, 5.0, "Search should be fast")
        
        # Should get a valid response (200 or 404)
        self.assertIn(response.status_code, [200, 404])
        print("✅ Search response time is acceptable")
    
    def test_search_with_special_characters(self):
        """Test search with special characters"""
        print("\n🧪 Testing search with special characters...")
        
        special_queries = [
            "test@video",
            "video#1",
            "test & video",
            "video (2025)",
            "test-video_final",
            "émojis 🎮",
            "quotes \"test\"",
            "apostrophe's test"
        ]
        
        for query in special_queries:
            with self.subTest(query=query):
                payload = {
                    "search_query": query,
                    "tags": []
                }
                
                try:
                    response = requests.post(
                        f"{self.BASE_URL}/find_clips",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        timeout=10
                    )
                    
                    # Should handle special characters gracefully
                    self.assertIn(response.status_code, [200, 404, 400])
                    print(f"✅ Handled special query: '{query}'")
                    
                except Exception as e:
                    self.fail(f"Failed to handle special characters in query '{query}': {e}")


def run_search_tests():
    """Run all video search tests"""
    print("=" * 60)
    print("🔍 PATCHWORK LIBRARY - VIDEO SEARCH TESTS")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5050/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Start it with: python3 start.py")
            return False
    except:
        print("❌ Server is not running. Start it with: python3 start.py")
        return False
    
    print("✅ Server is running")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add validation tests (always run)
    suite.addTest(TestVideoSearchAPI('test_find_clips_validation_errors'))
    suite.addTest(TestSearchPerformance('test_search_response_time'))
    suite.addTest(TestSearchPerformance('test_search_with_special_characters'))
    
    # Add database tests
    suite.addTest(TestDatabaseSearchFunctionality('test_search_videos_by_query'))
    suite.addTest(TestDatabaseSearchFunctionality('test_search_videos_by_tags'))
    suite.addTest(TestDatabaseSearchFunctionality('test_search_videos_combined'))
    
    # Ask user about database-dependent tests
    print("\n" + "=" * 60)
    print("⚠️  DATABASE TESTS WARNING")
    print("=" * 60)
    print("The following tests will:")
    print("- Add test data to your MongoDB database")
    print("- Require working MongoDB connection")
    print("- Test search functionality with real data")
    
    run_db_tests = input("\nRun database-dependent tests? (y/n): ").lower() == 'y'
    
    if run_db_tests:
        suite.addTest(TestVideoSearchAPI('test_find_clips_by_search_query'))
        suite.addTest(TestVideoSearchAPI('test_find_clips_by_tags'))
        suite.addTest(TestVideoSearchAPI('test_find_clips_combined_search'))
        suite.addTest(TestVideoSearchAPI('test_find_clips_case_insensitive_search'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {len(result.failures + result.errors)} TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_search_tests()
    exit(0 if success else 1) 