#!/usr/bin/env python3
"""
Dependency fixer for the video analysis system.
Resolves pyOpenSSL/cryptography compatibility issues.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def fix_dependencies():
    """Fix the pyOpenSSL/cryptography compatibility issue."""
    print("🔧 Fixing dependency compatibility issues...")
    
    # Step 1: Uninstall conflicting packages
    packages_to_remove = [
        'pyOpenSSL',
        'cryptography',
        'pymongo'
    ]
    
    for package in packages_to_remove:
        run_command(f"pip uninstall -y {package}", f"Uninstalling {package}")
    
    # Step 2: Install compatible versions
    compatible_packages = [
        'cryptography==41.0.8',
        'pyOpenSSL==23.3.0',
        'pymongo==4.6.0'
    ]
    
    for package in compatible_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"Failed to install {package}")
            return False
    
    # Step 3: Install remaining requirements
    if os.path.exists('requirements.txt'):
        if not run_command("pip install -r requirements.txt", "Installing remaining requirements"):
            print("Failed to install requirements")
            return False
    
    print("\n✅ Dependency issues fixed successfully!")
    return True

def verify_installation():
    """Verify that the installation works."""
    print("\n🔍 Verifying installation...")
    
    try:
        import pymongo
        print("✓ pymongo imported successfully")
        
        from pymongo import MongoClient
        print("✓ MongoClient imported successfully")
        
        import OpenSSL
        print("✓ OpenSSL imported successfully")
        
        print("\n✅ All dependencies are working correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Video Analysis System - Dependency Fixer")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Fix dependencies
    if not fix_dependencies():
        print("\n❌ Failed to fix dependencies")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nYou can now run the application with:")
    print("  python app.py")

if __name__ == "__main__":
    main() 