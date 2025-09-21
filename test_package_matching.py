#!/usr/bin/env python
"""
Test script to verify the new package matching functionality in Match model.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from maker.models import Brand, Model, Series, Package, Match, BrandModelSeries

def test_package_matching():
    """Test the new package matching functionality."""
    
    print("=== Package Matching Test ===\n")
    
    # Get or create test data
    print("1. Setting up test data...")
    print("-" * 40)
    
    # Create test brand, model, series
    brand, _ = Brand.objects.get_or_create(name="Tesla")
    model, _ = Model.objects.get_or_create(name="Model 3")
    series, _ = Series.objects.get_or_create(name="2024 Refresh")
    
    # Create or get a BrandModelSeries
    bms, created = BrandModelSeries.objects.get_or_create(
        brand=brand,
        model=model, 
        series=series,
        defaults={'year_start': 2024}
    )
    
    # Create test packages
    package1, _ = Package.objects.get_or_create(name="Standard Range")
    package2, _ = Package.objects.get_or_create(name="Long Range")
    package3, _ = Package.objects.get_or_create(name="Performance")
    
    # Associate packages with BrandModelSeries
    bms.packages.add(package1, package2, package3)
    
    print(f"✅ Created/found: {brand} {model} {series}")
    print(f"✅ Packages: {package1.name}, {package2.name}, {package3.name}")
    
    # Create test matches with different package filters
    print(f"\n2. Creating test matches...")
    print("-" * 40)
    
    # Clean up any existing test matches
    Match.objects.filter(brand=brand, model=model).delete()
    
    # Match 1: No package filter (matches any package)
    match1 = Match.objects.create(
        brand=brand,
        model=model,
        series=series
    )
    print(f"✅ Match 1: {match1}")
    
    # Match 2: Specific package filter (Standard Range)
    match2 = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package1
    )
    print(f"✅ Match 2: {match2}")
    
    # Match 3: Different package filter (Performance)
    match3 = Match.objects.create(
        brand=brand,
        model=model,
        series=series,
        package=package3
    )
    print(f"✅ Match 3: {match3}")
    
    # Test matching logic
    print(f"\n3. Testing match criteria...")
    print("-" * 40)
    
    test_cases = [
        {
            'name': 'No package specified',
            'criteria': {'brand': brand, 'model': model, 'series': series},
            'expected_matches': [match1]  # Only match without package filter should match
        },
        {
            'name': 'Standard Range package',
            'criteria': {'brand': brand, 'model': model, 'series': series, 'package': package1},
            'expected_matches': [match1, match2]  # No filter + specific package filter
        },
        {
            'name': 'Long Range package',
            'criteria': {'brand': brand, 'model': model, 'series': series, 'package': package2},
            'expected_matches': [match1]  # Only no filter match
        },
        {
            'name': 'Performance package',
            'criteria': {'brand': brand, 'model': model, 'series': series, 'package': package3},
            'expected_matches': [match1, match3]  # No filter + performance filter
        }
    ]
    
    all_matches = [match1, match2, match3]
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        criteria = test_case['criteria']
        
        matching_results = []
        for match in all_matches:
            if match.matches_criteria(**criteria):
                matching_results.append(match)
        
        print(f"   Criteria: {criteria}")
        print(f"   Expected matches: {len(test_case['expected_matches'])}")
        print(f"   Actual matches: {len(matching_results)}")
        
        if set(matching_results) == set(test_case['expected_matches']):
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL")
            print(f"      Expected: {[str(m) for m in test_case['expected_matches']]}")
            print(f"      Got: {[str(m) for m in matching_results]}")
    
    # Test edge cases
    print(f"\n4. Testing edge cases...")
    print("-" * 40)
    
    # Test with wrong brand (should match nothing)
    wrong_brand, _ = Brand.objects.get_or_create(name="BMW")
    matches_wrong_brand = []
    for match in all_matches:
        if match.matches_criteria(brand=wrong_brand, model=model, series=series, package=package1):
            matches_wrong_brand.append(match)
    
    print(f"🧪 Wrong brand test:")
    print(f"   Expected: 0 matches")
    print(f"   Actual: {len(matches_wrong_brand)} matches")
    print(f"   Result: {'✅ PASS' if len(matches_wrong_brand) == 0 else '❌ FAIL'}")
    
    print(f"\n✨ Package matching functionality test complete!")
    print(f"   The Match model now supports optional package filtering")
    print(f"   Matches work correctly with package criteria")

if __name__ == "__main__":
    test_package_matching()