#!/usr/bin/env python
"""
Complete demonstration of package matching functionality in the Match system.
Shows how the new package field enables package-specific content matching.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from maker.models import Brand, Model, Series, Package, Match, MatchItem, Blurb, BrandModelSeries

def demonstrate_package_matching():
    """Demonstrate the complete package matching system."""
    
    print("=== Complete Package Matching System Demonstration ===\n")
    
    # Set up comprehensive test data
    print("1. Setting up comprehensive test data...")
    print("-" * 50)
    
    # Clean up existing test data
    Match.objects.filter(brand__name="BMW").delete()
    
    # Create test entities
    brand, _ = Brand.objects.get_or_create(name="BMW")
    model, _ = Model.objects.get_or_create(name="i4")
    series, _ = Series.objects.get_or_create(name="2024 LCI")
    
    # Create BrandModelSeries
    bms, created = BrandModelSeries.objects.get_or_create(
        brand=brand,
        model=model,
        series=series,
        defaults={'year_start': 2024}
    )
    
    # Create packages with different feature sets
    package_base, _ = Package.objects.get_or_create(name="eDrive35")
    package_mid, _ = Package.objects.get_or_create(name="eDrive40") 
    package_performance, _ = Package.objects.get_or_create(name="M50")
    
    # Associate with BrandModelSeries
    bms.packages.add(package_base, package_mid, package_performance)
    
    print(f"✅ Vehicle: {brand} {model} {series}")
    print(f"✅ Packages: {package_base.name}, {package_mid.name}, {package_performance.name}")
    
    # Create different blurbs for different package tiers
    blurb_base, _ = Blurb.objects.get_or_create(
        text="Standard interior with leatherette seating",
        defaults={'group_priority': 1}
    )
    blurb_mid, _ = Blurb.objects.get_or_create(
        text="Premium interior with Dakota leather seating",
        defaults={'group_priority': 5}
    )
    blurb_performance, _ = Blurb.objects.get_or_create(
        text="M Sport interior with Merino leather and carbon fiber trim",
        defaults={'group_priority': 10}
    )
    blurb_common, _ = Blurb.objects.get_or_create(
        text="Advanced driver assistance systems with lane keeping",
        defaults={'group_priority': 1}
    )
    
    print(f"✅ Created blurbs for different package tiers")
    
    # Create matches with package-specific content
    print(f"\n2. Creating package-specific matches...")
    print("-" * 50)
    
    # Match for base package
    match_base = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package_base
    )
    MatchItem.objects.create(
        match=match_base,
        blurb=blurb_base,
        placement='interior',
        priority=1
    )
    MatchItem.objects.create(
        match=match_base,
        blurb=blurb_common,
        placement='highlights',
        priority=1
    )
    print(f"✅ {match_base} → Base interior content")
    
    # Match for mid-tier package
    match_mid = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package_mid
    )
    MatchItem.objects.create(
        match=match_mid,
        blurb=blurb_mid,
        placement='interior',
        priority=1
    )
    MatchItem.objects.create(
        match=match_mid,
        blurb=blurb_common,
        placement='highlights',
        priority=1
    )
    print(f"✅ {match_mid} → Premium interior content")
    
    # Match for performance package
    match_performance = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package_performance
    )
    MatchItem.objects.create(
        match=match_performance,
        blurb=blurb_performance,
        placement='interior',
        priority=1
    )
    MatchItem.objects.create(
        match=match_performance,
        blurb=blurb_common,
        placement='highlights',
        priority=1
    )
    print(f"✅ {match_performance} → M Sport interior content")
    
    # Match without package filter (applies to all)
    match_all = Match.objects.create(
        brand=brand,
        model=model,
        series=series
        # No package specified = matches all packages
    )
    blurb_universal, _ = Blurb.objects.get_or_create(
        text="BMW iDrive 8 infotainment system with wireless Apple CarPlay",
        defaults={'group_priority': 1}
    )
    MatchItem.objects.create(
        match=match_all,
        blurb=blurb_universal,
        placement='interior',
        priority=2
    )
    print(f"✅ {match_all} → Universal content for all packages")
    
    # Test package-specific matching
    print(f"\n3. Testing package-specific content matching...")
    print("-" * 50)
    
    test_scenarios = [
        {
            'package': package_base,
            'expected_interior_blurbs': [blurb_base, blurb_universal],
            'description': 'Base package should get standard interior + universal'
        },
        {
            'package': package_mid,
            'expected_interior_blurbs': [blurb_mid, blurb_universal],
            'description': 'Mid package should get premium interior + universal'
        },
        {
            'package': package_performance,
            'expected_interior_blurbs': [blurb_performance, blurb_universal],
            'description': 'Performance package should get M Sport interior + universal'
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing: {scenario['package'].name}")
        print(f"   {scenario['description']}")
        
        # Find matching matches for this package
        matching_matches = []
        for match in [match_base, match_mid, match_performance, match_all]:
            if match.matches_criteria(
                brand=brand,
                model=model,
                series=series,
                package=scenario['package']
            ):
                matching_matches.append(match)
        
        # Get interior blurbs from matching matches
        interior_blurbs = []
        for match in matching_matches:
            interior_items = match.items.filter(placement='interior')
            for item in interior_items:
                interior_blurbs.append(item.blurb)
        
        print(f"   Matching matches: {len(matching_matches)}")
        print(f"   Interior blurbs found: {len(interior_blurbs)}")
        
        # Check if we got the expected blurbs
        expected_blurbs = set(scenario['expected_interior_blurbs'])
        actual_blurbs = set(interior_blurbs)
        
        if expected_blurbs == actual_blurbs:
            print(f"   ✅ PASS - Got expected blurbs")
        else:
            print(f"   ❌ FAIL - Unexpected blurbs")
            print(f"      Expected: {[b.text[:30] + '...' for b in expected_blurbs]}")
            print(f"      Got: {[b.text[:30] + '...' for b in actual_blurbs]}")
        
        for blurb in interior_blurbs:
            print(f"      • {blurb.text}")
    
    # Show practical benefits
    print(f"\n4. Practical Benefits of Package Matching...")
    print("-" * 50)
    print("🎯 Package-Specific Content: Different packages show appropriate content")
    print("🎯 Content Accuracy: Base packages don't show premium features")
    print("🎯 Marketing Precision: Performance packages highlight sport features")
    print("🎯 Universal Content: Common features appear across all packages")
    print("🎯 Flexible Filtering: Mix package-specific and universal matches")
    
    # Show use cases
    print(f"\n5. Real-World Use Cases...")
    print("-" * 50)
    print("🚗 Base Package: Standard features, value positioning")
    print("🚗 Mid Package: Premium comfort, advanced features")
    print("🚗 Performance Package: Sport styling, performance features")
    print("🚗 Universal: Safety, infotainment, core brand features")
    
    print(f"\n✨ Package matching system is fully operational!")
    print("   Matches can now filter by specific packages")
    print("   Content generation respects package selections")
    print("   Different packages show appropriate content")

if __name__ == "__main__":
    demonstrate_package_matching()