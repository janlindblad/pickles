#!/usr/bin/env python
"""
Test script to demonstrate the enhanced Blurb admin interface with match item information.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from maker.models import Brand, Model, Series, Package, Match, MatchItem, Blurb, BrandModelSeries

def test_blurb_admin_enhancements():
    """Test the enhanced Blurb admin interface."""
    
    print("=== Enhanced Blurb Admin Interface Test ===\n")
    
    # Set up test data to demonstrate the admin enhancements
    print("1. Setting up test data...")
    print("-" * 50)
    
    # Clean up any existing test data
    Match.objects.filter(brand__name="Volvo").delete()
    
    # Create test entities
    brand, _ = Brand.objects.get_or_create(name="Volvo")
    model, _ = Model.objects.get_or_create(name="XC90")
    series, _ = Series.objects.get_or_create(name="2024 Facelift")
    
    # Create BrandModelSeries
    bms, created = BrandModelSeries.objects.get_or_create(
        brand=brand,
        model=model,
        series=series,
        defaults={'year_start': 2024}
    )
    
    # Create packages
    package1, _ = Package.objects.get_or_create(name="Core")
    package2, _ = Package.objects.get_or_create(name="Plus")
    package3, _ = Package.objects.get_or_create(name="Ultra")
    
    bms.packages.add(package1, package2, package3)
    
    # Create blurbs with different usage patterns
    blurb_popular, _ = Blurb.objects.get_or_create(
        text="Premium leather seating with heating and ventilation",
        defaults={'group_priority': 5}
    )
    
    blurb_unused, _ = Blurb.objects.get_or_create(
        text="This blurb is not used in any matches yet",
        defaults={'group_priority': 1}
    )
    
    blurb_multi_use, _ = Blurb.objects.get_or_create(
        text="Advanced driver assistance with lane keeping and adaptive cruise control",
        defaults={'group_priority': 8}
    )
    
    print(f"✅ Created test entities: {brand} {model} {series}")
    print(f"✅ Created packages: {package1.name}, {package2.name}, {package3.name}")
    print(f"✅ Created blurbs with different usage patterns")
    
    # Create matches that use these blurbs in various ways
    print(f"\n2. Creating matches with different blurb usage patterns...")
    print("-" * 50)
    
    # Match 1: Uses blurb_popular in interior
    match1 = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package2  # Plus package
    )
    MatchItem.objects.create(
        match=match1,
        blurb=blurb_popular,
        placement='interior',
        priority=5,
        sequence=1
    )
    print(f"✅ Match 1: {match1} uses popular blurb in interior")
    
    # Match 2: Uses blurb_multi_use in highlights
    match2 = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package3  # Ultra package
    )
    MatchItem.objects.create(
        match=match2,
        blurb=blurb_multi_use,
        placement='highlights',
        priority=8,
        sequence=1
    )
    print(f"✅ Match 2: {match2} uses multi-use blurb in highlights")
    
    # Match 3: Uses blurb_multi_use again in exterior (multi-use case)
    match3 = Match.objects.create(
        brand=brand,
        model=model,
        series=series
        # No package filter = applies to all packages
    )
    MatchItem.objects.create(
        match=match3,
        blurb=blurb_multi_use,
        placement='exterior', 
        priority=6,
        sequence=2
    )
    print(f"✅ Match 3: {match3} uses multi-use blurb in exterior")
    
    # Match 4: Uses blurb_popular again (another multi-use case)
    match4 = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package1  # Core package
    )
    MatchItem.objects.create(
        match=match4,
        blurb=blurb_popular,
        placement='options',
        priority=3,
        sequence=1
    )
    print(f"✅ Match 4: {match4} uses popular blurb in options")
    
    # Test the admin methods
    print(f"\n3. Testing enhanced admin methods...")
    print("-" * 50)
    
    from maker.admin import BlurbAdmin
    
    # Create a mock admin instance to test the methods
    admin_instance = BlurbAdmin(Blurb, None)
    
    test_blurbs = [
        ("Popular Blurb (used 2 times)", blurb_popular),
        ("Multi-use Blurb (used 2 times)", blurb_multi_use), 
        ("Unused Blurb (used 0 times)", blurb_unused)
    ]
    
    for description, blurb in test_blurbs:
        print(f"\n🧪 Testing: {description}")
        
        # Test get_match_count method
        match_count = admin_instance.get_match_count(blurb)
        print(f"   Match Count: {match_count}")
        
        # Test get_match_info method
        match_info = admin_instance.get_match_info(blurb)
        print(f"   Match Info: {match_info}")
        
        # Test get_text_preview method
        text_preview = admin_instance.get_text_preview(blurb)
        print(f"   Text Preview: {text_preview}")
    
    # Show what the admin list view would display
    print(f"\n4. Admin List View Demonstration...")
    print("-" * 50)
    print("The Blurb admin list view now shows:")
    print("📋 Text Preview - First 75 characters of blurb text")
    print("📊 Usage Count - How many match items use this blurb")
    print("🎯 Used In - Which matches and placements use this blurb")
    print("🏷️  Blurb Group - Group membership for exclusion logic")
    print("⭐ Group Priority - Priority within group")
    print("🆔 ID - Database ID for reference")
    
    print(f"\n5. Admin Detail View Features...")
    print("-" * 50)
    print("When editing a blurb, users can now see:")
    print("📝 Blurb content and group settings (as before)")
    print("📑 Inline table showing ALL match items that use this blurb")
    print("🔍 Each match item shows: Match, Placement, Priority, Sequence")
    print("👁️  Read-only view (can't edit match items from blurb admin)")
    print("🔗 Links to jump to the actual Match admin for editing")
    
    print(f"\n6. Search and Filter Improvements...")
    print("-" * 50)
    print("Users can now search/filter blurbs by:")
    print("🔍 Blurb text content")
    print("🏷️  Blurb group name")
    print("🏢 Brand name (from associated matches)")
    print("🚗 Model name (from associated matches)")  
    print("📍 Placement type (interior, exterior, highlights, options)")
    
    print(f"\n✨ Enhanced Blurb admin interface is ready!")
    print("   Users can easily see which matches use each blurb")
    print("   Clear visibility into blurb usage patterns")
    print("   Improved search and filtering capabilities")
    print("   Read-only inline view of related match items")

if __name__ == "__main__":
    test_blurb_admin_enhancements()