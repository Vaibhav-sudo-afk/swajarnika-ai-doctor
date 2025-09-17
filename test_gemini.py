#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""
import sys
import os

try:
    import google.generativeai as genai
    print("✓ Google Generative AI library imported successfully")
    
    # Configure Gemini API
    GEMINI_API_KEY = "AIzaSyC6APklLc0G9Ts1KecMXXwUKUsk_gGzF48"
    genai.configure(api_key=GEMINI_API_KEY)
    print("✓ API key configured")
    
    # Test API connectivity
    try:
        models = genai.list_models()
        available_models = list(models)
        print(f"✓ API connectivity successful. Found {len(available_models)} models")
        
        # Test a simple chat
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello! Please respond with a simple greeting.")
        print(f"✓ Test chat successful: {response.text[:100]}...")
        
        print("\n🎉 Gemini API integration is working correctly!")
        
    except Exception as e:
        print(f"❌ API connectivity test failed: {e}")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Failed to import Google Generative AI library: {e}")
    print("Make sure you have installed: pip install google-generativeai")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)