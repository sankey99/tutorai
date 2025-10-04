#!/usr/bin/env python3
"""
Test script for OAuth implementation.
This script helps verify that the OAuth setup is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_oauth_config():
    """Test OAuth configuration."""
    print("🔍 Testing OAuth Configuration...")
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Check required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'GOOGLE_CLIENT_ID', 
        'GOOGLE_CLIENT_SECRET',
        'GOOGLE_REDIRECT_URI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please add these to your .env file:")
        print("OPENAI_API_KEY=your_openai_key_here")
        print("GOOGLE_CLIENT_ID=your_google_client_id_here")
        print("GOOGLE_CLIENT_SECRET=your_google_client_secret_here")
        print("GOOGLE_REDIRECT_URI=http://localhost:7860/auth/callback")
        return False
    
    print("✅ All required environment variables found")
    
    # Test imports
    try:
        from auth import GoogleOAuth, create_oauth_app
        print("✅ OAuth module imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        return False
    
    # Test OAuth class initialization
    try:
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        oauth = GoogleOAuth(client_id, client_secret, redirect_uri)
        print("✅ OAuth class initialized successfully")
        
        # Test authorization URL generation
        auth_url = oauth.get_authorization_url()
        if auth_url and 'accounts.google.com' in auth_url:
            print("✅ Authorization URL generated successfully")
        else:
            print("❌ Invalid authorization URL generated")
            return False
            
    except Exception as e:
        print(f"❌ OAuth initialization error: {e}")
        return False
    
    print("\n🎉 OAuth configuration test passed!")
    print("\n📋 Next steps:")
    print("1. Make sure your Google OAuth credentials are correctly configured")
    print("2. Run the app with: python app.py --oauth")
    print("3. Test the authentication flow in your browser")
    
    return True

def test_dependencies():
    """Test if all required dependencies are installed."""
    print("🔍 Testing Dependencies...")
    
    required_packages = [
        'gradio',
        'openai', 
        'python-dotenv',
        'requests',
        'beautifulsoup4',
        'authlib',
        'flask'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def main():
    """Run all tests."""
    print("🚀 TutorAI OAuth Test Suite")
    print("=" * 40)
    
    # Test dependencies first
    if not test_dependencies():
        sys.exit(1)
    
    print()
    
    # Test OAuth configuration
    if not test_oauth_config():
        sys.exit(1)
    
    print("\n🎉 All tests passed! Your OAuth setup is ready.")
    print("\n🚀 You can now run:")
    print("   python app.py --oauth")

if __name__ == "__main__":
    main()
