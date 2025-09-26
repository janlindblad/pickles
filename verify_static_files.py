#!/usr/bin/env python
"""
Verification script to confirm CSS files are properly moved and configured.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles.finders import find

def main():
    print("=== Static Files Configuration Verification ===\n")
    
    # Check directory structure
    print("📁 Directory Structure Check:")
    print("-" * 40)
    
    expected_css_files = [
        'base.css',
        'components.css', 
        'layout.css',
        'components-specific.css'
    ]
    
    css_dir = 'maker/static/maker/css'
    if os.path.exists(css_dir):
        print(f"✅ {css_dir}/ exists")
        
        for css_file in expected_css_files:
            full_path = os.path.join(css_dir, css_file)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  ✅ {css_file} ({size:,} bytes)")
            else:
                print(f"  ❌ {css_file} (missing)")
    else:
        print(f"❌ {css_dir}/ does not exist")
    
    # Check Django static files configuration
    print(f"\n⚙️  Django Static Files Settings:")
    print("-" * 40)
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {getattr(settings, 'STATIC_ROOT', 'Not set')}")
    print(f"STATICFILES_DIRS: {getattr(settings, 'STATICFILES_DIRS', [])}")
    
    # Test static file finding
    print(f"\n🔍 Static File Finding Test:")
    print("-" * 40)
    
    for css_file in expected_css_files:
        static_path = f'maker/css/{css_file}'
        found_path = find(static_path)
        
        if found_path:
            print(f"✅ {static_path} → {found_path}")
        else:
            print(f"❌ {static_path} (not found by Django)")
    
    # Check template references
    print(f"\n📄 Template Reference Check:")
    print("-" * 40)
    
    template_file = 'templates/base_header.html'
    if os.path.exists(template_file):
        with open(template_file, 'r') as f:
            content = f.read()
        
        print(f"✅ {template_file} exists")
        
        # Check for correct static references
        expected_refs = [
            "{% static 'maker/css/base.css' %}",
            "{% static 'maker/css/components.css' %}",
            "{% static 'maker/css/layout.css' %}",
            "{% static 'maker/css/components-specific.css' %}"
        ]
        
        for ref in expected_refs:
            if ref in content:
                print(f"  ✅ Found: {ref}")
            else:
                print(f"  ❌ Missing: {ref}")
    else:
        print(f"❌ {template_file} not found")
    
    # Check old static directory
    print(f"\n🧹 Cleanup Check:")
    print("-" * 40)
    
    old_static_dir = 'static'
    if os.path.exists(old_static_dir):
        static_contents = os.listdir(old_static_dir)
        if static_contents:
            print(f"⚠️  {old_static_dir}/ contains files (should be empty or not in git)")
            for item in static_contents[:5]:  # Show first 5 items
                print(f"     - {item}")
            if len(static_contents) > 5:
                print(f"     ... and {len(static_contents) - 5} more")
        else:
            print(f"✅ {old_static_dir}/ is empty (good for collectstatic)")
    else:
        print(f"ℹ️  {old_static_dir}/ doesn't exist")
    
    # Final status
    print(f"\n✨ Configuration Status:")
    print("-" * 40)
    
    # Test if collectstatic would work
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('collectstatic', '--dry-run', '--noinput', stdout=out, verbosity=0)
        print("✅ collectstatic dry-run: SUCCESS")
    except Exception as e:
        print(f"❌ collectstatic dry-run: FAILED ({e})")
    
    print(f"\n🎯 Next Steps:")
    print("-" * 40)
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://localhost:8000/")
    print("3. Check browser dev tools for CSS loading")
    print("4. For production: python manage.py collectstatic")
    
    print(f"\n📋 Static Files Structure (Correct):")
    print("-" * 40)
    print("maker/")
    print("└── static/")
    print("    └── maker/          # ← App namespace")
    print("        └── css/")
    print("            ├── base.css")
    print("            ├── components.css")
    print("            ├── layout.css")
    print("            └── components-specific.css")

if __name__ == "__main__":
    main()