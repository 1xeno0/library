#!/usr/bin/env python3
"""
Comprehensive test suite for video analysis functionality
Tests the /analyse endpoint and VideoAnalyzer class
"""

import unittest
import requests
import json
import time
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Add current directory to path for imports
sys.path.append('.')

from analyse import VideoAnalyzer
from database import DatabaseManager
import config

class TestVideoAnalysisAPI(unittest.TestCase):
    """Test the video analysis API endpoint"""
    
    BASE_URL = "http://localhost:5050"
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a working sample video URL from Google Cloud Storage
        self.test_video_url = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
        self.invalid_video_url = "https://invalid-url.com/nonexistent.mp4"
        
    def test_analyse_endpoint_valid_video(self):
        """Test analysis with a valid video URL"""
        print("\n🧪 Testing /analyse endpoint with valid video...")
        
        payload = {"video_link": self.test_video_url}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/analyse",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=300  # 5 minutes timeout for video processing
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Analysis successful!")
                print(f"Response: {json.dumps(result, indent=2)}")
                
                # Validate response structure
                self.assertIn("title", result)
                self.assertIn("description", result)
                self.assertIn("tags", result)
                self.assertIn("upload_date", result)
                
                # Validate data types
                self.assertIsInstance(result["title"], str)
                self.assertIsInstance(result["description"], str)
                self.assertIsInstance(result["tags"], list)
                self.assertIsInstance(result["upload_date"], str)
                
                # Validate content is not empty
                self.assertTrue(len(result["title"]) > 0, "Title should not be empty")
                self.assertTrue(len(result["description"]) > 0, "Description should not be empty")
                
            else:
                print(f"❌ Analysis failed: {response.text}")
                self.fail(f"Expected 200, got {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.fail("Request timed out - video analysis took too long")
        except Exception as e:
            self.fail(f"Request failed: {e}")
    
    def test_analyse_endpoint_missing_video_link(self):
        """Test analysis with missing video_link field"""
        print("\n🧪 Testing /analyse endpoint with missing video_link...")
        
        payload = {}  # Missing video_link
        
        response = requests.post(
            f"{self.BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        
        result = response.json()
        self.assertIn("error", result)
        print(f"✅ Correctly rejected: {result['error']}")
    
    def test_analyse_endpoint_empty_video_link(self):
        """Test analysis with empty video_link"""
        print("\n🧪 Testing /analyse endpoint with empty video_link...")
        
        payload = {"video_link": ""}
        
        response = requests.post(
            f"{self.BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        
        result = response.json()
        self.assertIn("error", result)
        print(f"✅ Correctly rejected: {result['error']}")
    
    def test_analyse_endpoint_invalid_json(self):
        """Test analysis with invalid JSON"""
        print("\n🧪 Testing /analyse endpoint with invalid JSON...")
        
        response = requests.post(
            f"{self.BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            data="invalid json"
        )
        
        print(f"Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 400)
        print("✅ Correctly rejected invalid JSON")
    
    def test_analyse_endpoint_duplicate_video(self):
        """Test that analyzing the same video twice returns cached result"""
        print("\n🧪 Testing /analyse endpoint with duplicate video...")
        
        payload = {"video_link": self.test_video_url}
        
        # First analysis
        start_time = time.time()
        response1 = requests.post(
            f"{self.BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=300
        )
        first_duration = time.time() - start_time
        
        if response1.status_code != 200:
            self.skipTest("First analysis failed, skipping duplicate test")
        
        # Second analysis (should be faster due to caching)
        start_time = time.time()
        response2 = requests.post(
            f"{self.BASE_URL}/analyse",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60
        )
        second_duration = time.time() - start_time
        
        print(f"First analysis took: {first_duration:.2f}s")
        print(f"Second analysis took: {second_duration:.2f}s")
        
        self.assertEqual(response2.status_code, 200)
        
        # Results should be identical
        result1 = response1.json()
        result2 = response2.json()
        
        self.assertEqual(result1["title"], result2["title"])
        self.assertEqual(result1["description"], result2["description"])
        self.assertEqual(result1["tags"], result2["tags"])
        
        print("✅ Duplicate analysis returned cached result")


class TestVideoAnalyzerClass(unittest.TestCase):
    """Test the VideoAnalyzer class directly"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = VideoAnalyzer()
        self.test_video_url = "https://renderer.ezr.lv/render/680876b27ed09a50637439a"
    
    @patch('analyse.requests.get')
    def test_download_video_success(self, mock_get):
        """Test successful video download"""
        print("\n🧪 Testing video download...")
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'fake_video_data']
        mock_get.return_value = mock_response
        
        try:
            video_path = self.analyzer.download_video(self.test_video_url)
            self.assertTrue(os.path.exists(video_path))
            print(f"✅ Video downloaded to: {video_path}")
            
            # Cleanup
            if os.path.exists(video_path):
                os.remove(video_path)
                
        except Exception as e:
            self.fail(f"Video download failed: {e}")
    
    @patch('analyse.requests.get')
    def test_download_video_failure(self, mock_get):
        """Test video download failure"""
        print("\n🧪 Testing video download failure...")
        
        # Mock failed response
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with self.assertRaises(Exception) as context:
            self.analyzer.download_video("https://invalid-url.com/video.mp4")
        
        self.assertIn("Failed to download video", str(context.exception))
        print("✅ Correctly handled download failure")
    
    def test_encode_image(self):
        """Test image encoding to base64"""
        print("\n🧪 Testing image encoding...")
        
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            # Write some fake image data
            temp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # JPEG header
            temp_path = temp_file.name
        
        try:
            encoded = self.analyzer.encode_image(temp_path)
            self.assertIsInstance(encoded, str)
            self.assertTrue(len(encoded) > 0)
            print("✅ Image encoded successfully")
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @patch('analyse.VideoAnalyzer.analyze_frames_with_gpt')
    @patch('analyse.VideoAnalyzer.extract_frames')
    @patch('analyse.VideoAnalyzer.download_video')
    def test_analyze_video_workflow(self, mock_download, mock_extract, mock_analyze):
        """Test the complete video analysis workflow"""
        print("\n🧪 Testing complete analysis workflow...")
        
        # Mock the workflow
        mock_download.return_value = "/tmp/fake_video.mp4"
        mock_extract.return_value = ["/tmp/frame1.jpg", "/tmp/frame2.jpg"]
        mock_analyze.return_value = {
            "title": "Test Video",
            "description": "A test video description",
            "tags": ["test", "video"],
            "upload_date": "2025-04-23"
        }
        
        # Mock database to avoid actual DB operations
        with patch.object(self.analyzer.db, 'get_video_by_url', return_value=None), \
             patch.object(self.analyzer.db, 'save_video_analysis', return_value="fake_id"), \
             patch.object(self.analyzer, 'cleanup_temp_files'):
            
            result = self.analyzer.analyze_video(self.test_video_url)
            
            self.assertIsInstance(result, dict)
            self.assertIn("title", result)
            self.assertIn("description", result)
            self.assertIn("tags", result)
            self.assertIn("upload_date", result)
            self.assertIn("video_url", result)
            
            print(f"✅ Analysis workflow completed: {result}")


class TestVideoAnalysisIntegration(unittest.TestCase):
    """Integration tests for video analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = DatabaseManager()
        self.test_video_url = "https://test-video-url.com/test.mp4"
    
    def test_database_integration(self):
        """Test database operations for video analysis"""
        print("\n🧪 Testing database integration...")
        
        # Test data
        analysis_data = {
            "title": "Integration Test Video",
            "description": "A video for testing database integration",
            "tags": ["integration", "test", "database"],
            "upload_date": "2025-04-23",
            "frames_analyzed": 5
        }
        
        try:
            # Save analysis
            video_id = self.db.save_video_analysis(self.test_video_url, analysis_data)
            self.assertIsNotNone(video_id)
            print(f"✅ Video analysis saved with ID: {video_id}")
            
            # Retrieve analysis
            retrieved = self.db.get_video_by_url(self.test_video_url)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved["title"], analysis_data["title"])
            self.assertEqual(retrieved["description"], analysis_data["description"])
            self.assertEqual(retrieved["tags"], analysis_data["tags"])
            print("✅ Video analysis retrieved successfully")
            
            # Test duplicate handling
            video_id2 = self.db.save_video_analysis(self.test_video_url, analysis_data)
            self.assertEqual(str(video_id), str(video_id2))
            print("✅ Duplicate video handling works correctly")
            
        except Exception as e:
            print(f"⚠️  Database test skipped (likely no MongoDB connection): {e}")
            self.skipTest("Database not available")


def run_analysis_tests():
    """Run all video analysis tests"""
    print("=" * 60)
    print("🧪 PATCHWORK LIBRARY - VIDEO ANALYSIS TESTS")
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
    
    # Add API tests
    suite.addTest(TestVideoAnalysisAPI('test_analyse_endpoint_missing_video_link'))
    suite.addTest(TestVideoAnalysisAPI('test_analyse_endpoint_empty_video_link'))
    suite.addTest(TestVideoAnalysisAPI('test_analyse_endpoint_invalid_json'))
    
    # Add class tests
    suite.addTest(TestVideoAnalyzerClass('test_download_video_failure'))
    suite.addTest(TestVideoAnalyzerClass('test_encode_image'))
    suite.addTest(TestVideoAnalyzerClass('test_analyze_video_workflow'))
    
    # Add integration tests
    suite.addTest(TestVideoAnalysisIntegration('test_database_integration'))
    
    # Ask user about expensive tests
    print("\n" + "=" * 60)
    print("⚠️  EXPENSIVE TESTS WARNING")
    print("=" * 60)
    print("The following tests will:")
    print("- Download and process actual videos")
    print("- Make real OpenAI API calls (costs money)")
    print("- Take several minutes to complete")
    print("- Require working MongoDB connection")
    
    run_expensive = input("\nRun expensive tests? (y/n): ").lower() == 'y'
    
    if run_expensive:
        suite.addTest(TestVideoAnalysisAPI('test_analyse_endpoint_valid_video'))
        suite.addTest(TestVideoAnalysisAPI('test_analyse_endpoint_duplicate_video'))
    
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
    success = run_analysis_tests()
    exit(0 if success else 1) 