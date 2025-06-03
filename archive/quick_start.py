#!/usr/bin/env python3
"""
Quick start script for Patchwork Library Analyzer + Search API
Checks dependencies and starts the server
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'requests', 
        'openai',
        'pymongo',
        'moviepy',
        'PIL',  # Pillow
        'dotenv',  # python-dotenv
        'flask_cors',
        'dns'  # dnspython
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    else:
        print("✅ All dependencies are installed")
        return True

def create_directories():
    """Create necessary directories"""
    directories = ["temp", "temp/videos", "temp/frames"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def test_imports():
    """Test critical imports"""
    try:
        from moviepy import VideoFileClip
        print("✅ MoviePy import successful")
        
        from app import app
        print("✅ Flask app import successful")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Patchwork Library Analyzer + Search API...")
    print("📝 Note: MongoDB warnings are normal if you haven't configured a database")
    print("🌐 Server will be available at: http://localhost:5050")
    print("❤️  Health check: http://localhost:5050/health")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        from app import app
        import config
        app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main setup and start function"""
    print("=" * 60)
    print("🧪 PATCHWORK LIBRARY - QUICK START")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return False
    
    print("\n📁 Creating directories...")
    create_directories()
    
    print("\n🧪 Testing imports...")
    if not test_imports():
        return False
    
    print("\n✅ All checks passed!")
    
    # Ask user if they want to start the server
    start_choice = input("\nStart the server now? (y/n): ").lower()
    if start_choice == 'y':
        start_server()
    else:
        print("\n📝 To start the server manually, run: python3 app.py")
        print("📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 