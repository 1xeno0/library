#!/usr/bin/env python3
"""
Startup script for Patchwork Library Analyzer + Search API
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'requests', 'openai', 'pymongo', 
        'moviepy', 'pillow', 'python-dotenv', 'flask-cors'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_config():
    """Check if configuration is properly set"""
    try:
        import config
        
        # Check OpenAI API key
        if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
            print("❌ OpenAI API key not configured in config.py")
            return False
        print("✅ OpenAI API key configured")
        
        # Check MongoDB URI
        if not config.MONGODB_URI or "username:password" in config.MONGODB_URI:
            print("⚠️  MongoDB URI not configured - using default (may not work)")
            print("   Update MONGODB_URI in config.py or set as environment variable")
        else:
            print("✅ MongoDB URI configured")
        
        return True
        
    except ImportError:
        print("❌ config.py not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['temp', 'temp/frames', 'temp/videos']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def start_server():
    """Start the Flask server"""
    print("\n" + "=" * 50)
    print("Starting Patchwork Library Analyzer + Search API...")
    print("=" * 50)
    print("Server will be available at: http://localhost:5000")
    print("API Endpoints:")
    print("  POST /analyse     - Analyze video content")
    print("  POST /find_clips  - Search for clips")
    print("  GET  /health      - Health check")
    print("  GET  /videos      - List all videos")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")

def main():
    """Main startup function"""
    print("Patchwork Library Analyzer + Search API")
    print("=" * 50)
    print("Checking system requirements...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    print("\nChecking configuration...")
    if not check_config():
        print("\n⚠️  Configuration issues detected. The system may not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 