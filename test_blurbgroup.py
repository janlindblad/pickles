#!/usr/bin/env python
"""
Test script to demonstrate BlurbGroup exclusion/replacement functionality.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
django.setup()

from maker.models import BlurbGroup, Blurb, Match, MatchItem
from maker.views import _apply_blurb_group_logic

def test_blurbgroup_logic():
    """Test the BlurbGroup exclusion logic."""
    
    print("=== BlurbGroup Test ===")
    
    # Show current BlurbGroups
    print("\nBlurbGroups:")
    for group in BlurbGroup.objects.all():
        print(f"  {group.name} (max_items: {group.max_items})")
        for blurb in Blurb.objects.filter(blurb_group=group).order_by('-group_priority'):
            print(f"    - {blurb.text} (priority: {blurb.group_priority})")
    
    # Create some test MatchItems that include parking blurbs
    parking_group = BlurbGroup.objects.filter(name="Parking Assistance").first()
    if parking_group:
        print(f"\n=== Testing {parking_group.name} Group ===")
        
        # Get all blurbs in the parking group
        parking_blurbs = Blurb.objects.filter(blurb_group=parking_group)
        print(f"Blurbs in group: {parking_blurbs.count()}")
        
        # Create mock MatchItems for testing
        mock_items = []
        for i, blurb in enumerate(parking_blurbs):
            class MockMatchItem:
                def __init__(self, blurb, priority=1, sequence=1):
                    self.blurb = blurb
                    self.priority = priority
                    self.sequence = sequence
            
            mock_items.append(MockMatchItem(blurb, priority=1, sequence=i))
        
        print(f"\nBefore BlurbGroup logic (should show all {len(mock_items)} items):")
        for item in mock_items:
            print(f"  - {item.blurb.text} (group_priority: {item.blurb.group_priority})")
        
        # Apply BlurbGroup logic
        filtered_items = _apply_blurb_group_logic(mock_items)
        
        print(f"\nAfter BlurbGroup logic (should show only {parking_group.max_items} item):")
        for item in filtered_items:
            print(f"  - {item.blurb.text} (group_priority: {item.blurb.group_priority})")
        
        print(f"\nExpected result: Only 'Automatic parking' should appear (highest priority: 10)")
        
    else:
        print("No Parking Assistance group found - please run Django shell commands first")

if __name__ == "__main__":
    test_blurbgroup_logic()