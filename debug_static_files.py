#!/usr/bin/env python
"""
Debug script to diagnose static files serving issues.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find, get_finders
from django.test import Client
from django.urls import reverse

def main():
    print("=== Static Files Debug Information ===\n")
    
    # Check Django settings
    print("🔧 Django Settings:")
    print("-" * 30)
    print(f"DEBUG = {settings.DEBUG}")
    print(f"STATIC_URL = '{settings.STATIC_URL}'")
    print(f"STATIC_ROOT = {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS = {settings.STATICFILES_DIRS}")
    print(f"INSTALLED_APPS includes staticfiles = {'django.contrib.staticfiles' in settings.INSTALLED_APPS}")
    
    # Check static files finders
    print(f"\n🔍 Static Files Finders:")
    print("-" * 30)
    for finder in get_finders():
        print(f"✅ {finder.__class__.__name__}")
        if hasattr(finder, 'locations'):
            for location in finder.locations:
                print(f"   📁 {location}")
    
    # Test finding our CSS files
    css_files = [
        'maker/css/base.css',
        'maker/css/components.css',
        'maker/css/layout.css',
        'maker/css/components-specific.css'
    ]
    
    print(f"\n📄 CSS File Location Test:")
    print("-" * 30)
    for css_file in css_files:
        found_path = find(css_file)
        if found_path:
            print(f"✅ {css_file} → {found_path}")
        else:
            print(f"❌ {css_file} → NOT FOUND")
    
    # Test the development server static file serving
    print(f"\n🌐 Static File URL Test:")
    print("-" * 30)
    
    client = Client()
    
    for css_file in css_files:
        url = f"{settings.STATIC_URL}{css_file}"
        print(f"Testing: {url}")
        
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✅ Status: {response.status_code} (OK)")
                print(f"  📄 Content-Type: {response.get('Content-Type', 'Not set')}")
                content_length = len(response.content)
                print(f"  📏 Content-Length: {content_length} bytes")
            else:
                print(f"  ❌ Status: {response.status_code}")
        except Exception as e:
            print(f"  💥 Error: {e}")
        print()
    
    # Check if staticfiles app is properly configured
    print(f"🔧 StaticFiles App Configuration:")
    print("-" * 30)
    
    try:
        from django.contrib.staticfiles.apps import StaticFilesConfig
        print("✅ StaticFiles app is available")
    except ImportError:
        print("❌ StaticFiles app is not available")
    
    # Check middleware
    print(f"\n🔧 Middleware Check:")
    print("-" * 30)
    staticfiles_middleware = any('staticfiles' in middleware.lower() for middleware in settings.MIDDLEWARE)
    print(f"StaticFiles middleware detected: {staticfiles_middleware}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    print("-" * 30)
    
    if not settings.DEBUG:
        print("⚠️  DEBUG is False - static files won't be served by Django development server")
        print("   Set DEBUG = True in settings for development")
    
    if 'django.contrib.staticfiles' not in settings.INSTALLED_APPS:
        print("⚠️  django.contrib.staticfiles is not in INSTALLED_APPS")
        print("   Add 'django.contrib.staticfiles' to INSTALLED_APPS")
    
    if not css_files or not any(find(css) for css in css_files):
        print("⚠️  CSS files not found by Django static files system")
        print("   Check that files are in maker/static/maker/css/ directory")
    
    print(f"\n🎯 Quick Test:")
    print("-" * 30)
    print("1. Ensure DEBUG = True in settings")
    print("2. Start server: python manage.py runserver") 
    print("3. Visit: http://127.0.0.1:8000/static/maker/css/base.css")
    print("4. Should see CSS content, not 404 error")

if __name__ == "__main__":
    main()