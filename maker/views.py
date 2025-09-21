"""
Particularly Important Module

This module contains the core views for the maker application.
It handles the main user interface for creating ad blurbs and managing
product selections with real-time updates.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import models
import json

from .models import Brand, Model, Package, Year, Blurb, Match, BrandModelSeries, Series, MatchItem
from .constants import CONTENT_LIMITS, CONTENT_SEPARATOR, CONTENT_ENDING, MESSAGES, FALLBACK_CONTENT


def _apply_blurb_group_logic(items):
    """
    Apply BlurbGroup exclusion/replacement logic to a list of MatchItems.
    
    This function:
    1. Groups items by their blurb's BlurbGroup (if any)
    2. Within each group, selects only the highest priority items (up to max_items)
    3. Returns deduplicated items (same blurb never appears twice)
    
    Args:
        items: List of MatchItem objects
        
    Returns:
        List of MatchItem objects after applying group logic
    """
    # Separate grouped and ungrouped items
    grouped_items = {}  # blurb_group_id -> list of items
    ungrouped_items = []
    
    for item in items:
        if item.blurb.blurb_group:
            group_id = item.blurb.blurb_group.id
            if group_id not in grouped_items:
                grouped_items[group_id] = []
            grouped_items[group_id].append(item)
        else:
            ungrouped_items.append(item)
    
    # Process grouped items
    selected_items = []
    
    for group_id, group_items in grouped_items.items():
        # Get the BlurbGroup to check max_items
        blurb_group = group_items[0].blurb.blurb_group
        max_items = blurb_group.max_items
        
        # Sort by group_priority (descending) then by MatchItem priority/sequence
        sorted_group_items = sorted(
            group_items, 
            key=lambda x: (-x.blurb.group_priority, -x.priority, x.sequence)
        )
        
        # Select up to max_items from this group
        selected_items.extend(sorted_group_items[:max_items])
    
    # Add ungrouped items
    selected_items.extend(ungrouped_items)
    
    # Deduplicate by blurb_id (same blurb should never appear twice)
    seen_blurbs = set()
    deduplicated_items = []
    
    for item in selected_items:
        if item.blurb.id not in seen_blurbs:
            seen_blurbs.add(item.blurb.id)
            deduplicated_items.append(item)
    
    return deduplicated_items


def maker_start_view(request):
    """
    Main start page view for the Pickles maker application.
    
    Displays selection interface for Brand, Model, Year, and Packages.
    Provides responsive interface without form submission.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        HttpResponse with rendered start page template
    """
    # Get all available options for dropdowns
    brands = Brand.objects.all().order_by('name')
    models = Model.objects.all().order_by('name')  
    years = Year.objects.all().order_by('-year')  # Most recent first
    packages = Package.objects.all().order_by('name')
    
    context = {
        'brands': brands,
        'models': models,
        'years': years,
        'packages': packages,
        'page_title': 'Pickles Maker - Start',
    }
    
    return render(request, 'maker/start.html', context)


@require_http_methods(["GET"])
def maker_packages_api(request):
    """
    API endpoint to get packages based on Brand, Model, and Year selection.
    
    Uses BrandModelSeries to find packages available for the specific
    Brand+Model+Year combination.
    
    Args:
        request: Django HttpRequest object with GET parameters:
            - brand_id: ID of selected brand
            - model_id: ID of selected model  
            - year_id: ID of selected year
            
    Returns:
        JsonResponse with packages data
    """
    try:
        # Get selection parameters
        brand_id = request.GET.get('brand_id')
        model_id = request.GET.get('model_id')
        year_id = request.GET.get('year_id')
        
        # Validate required parameters
        if not all([brand_id, model_id, year_id]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters: brand_id, model_id, year_id'
            }, status=400)
        
        try:
            # Get the year object to get the integer value
            year_obj = Year.objects.get(id=year_id)
            year_int = year_obj.year
        except Year.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Year with id {year_id} not found'
            }, status=404)
        
        # Find BrandModelSeries that matches the selection
        series = BrandModelSeries.objects.filter(
            brand_id=brand_id,
            model_id=model_id,
            year_start__lte=year_int
        ).filter(
            models.Q(year_end__gte=year_int) | models.Q(year_end__isnull=True)
        ).first()
        
        if series:
            # Get packages that are associated with the matching series
            packages = Package.objects.filter(brand_model_series=series).order_by('name')
            series_info = {
                'id': series.id,
                'name': str(series),
                'year_range': series.get_year_display(),
            }
        else:
            # No matching series found, return empty package list
            packages = Package.objects.none()
            series_info = None
        
        packages_data = [
            {
                'id': package.id,
                'name': package.name,
            }
            for package in packages
        ]
        
        return JsonResponse({
            'success': True,
            'packages': packages_data,
            'series_info': series_info,
            'filter_applied': {
                'brand_id': brand_id,
                'model_id': model_id,
                'year_id': year_id,
                'year_value': year_int,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def maker_models_api(request):
    """
    API endpoint to get models based on Brand selection.
    
    Uses BrandModelSeries to find models available for the specific brand.
    
    Args:
        request: Django HttpRequest object with GET parameters:
            - brand_id: ID of selected brand
            
    Returns:
        JsonResponse with models data
    """
    try:
        # Get selection parameters
        brand_id = request.GET.get('brand_id')
        
        # Validate required parameters
        if not brand_id:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameter: brand_id'
            }, status=400)
        
        try:
            brand = Brand.objects.get(id=brand_id)
        except Brand.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Brand with id {brand_id} not found'
            }, status=404)
        
        # Get models for this brand from BrandModelSeries
        series_for_brand = BrandModelSeries.objects.filter(brand=brand).select_related('model')
        models_set = set()
        
        for series in series_for_brand:
            models_set.add((series.model.id, series.model.name))
        
        # Convert to sorted list of dictionaries
        models_data = [
            {
                'id': model_id,
                'name': model_name,
            }
            for model_id, model_name in sorted(models_set, key=lambda x: x[1])
        ]
        
        return JsonResponse({
            'success': True,
            'models': models_data,
            'brand_info': {
                'id': brand.id,
                'name': brand.name,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def maker_content_api(request):
    """
    API endpoint to generate content based on Brand, Model, Year, and Package selection.
    
    Finds matching Match instances based on selection criteria, collects associated
    MatchItems by placement category, applies priority-based selection with character
    limits, and returns generated content for all categories.
    
    Args:
        request: Django HttpRequest object with GET parameters:
            - brand_id: ID of selected brand (optional)
            - model_id: ID of selected model (optional) 
            - year_id: ID of selected year (optional)
            - package_id: ID of selected package (optional)
            
    Returns:
        JsonResponse with generated content for each placement category
    """
    try:
        # Get selection parameters
        brand_id = request.GET.get('brand_id')
        model_id = request.GET.get('model_id') 
        year_id = request.GET.get('year_id')
        package_id = request.GET.get('package_id')
        
        # Get objects from IDs (if provided)
        brand = None
        model = None
        year_obj = None
        year_int = None
        package = None
        series = None
        
        if brand_id:
            try:
                brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Brand with id {brand_id} not found'
                }, status=404)
        
        if model_id:
            try:
                model = Model.objects.get(id=model_id)
            except Model.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Model with id {model_id} not found'
                }, status=404)
        
        if year_id:
            try:
                year_obj = Year.objects.get(id=year_id)
                year_int = year_obj.year
            except Year.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Year with id {year_id} not found'
                }, status=404)
        
        if package_id:
            try:
                package = Package.objects.get(id=package_id)
            except Package.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'Package with id {package_id} not found'
                }, status=404)
        
        # If we have brand, model, and year, try to find the series
        if brand and model and year_int:
            brand_model_series = BrandModelSeries.objects.filter(
                brand=brand,
                model=model,
                year_start__lte=year_int
            ).filter(
                models.Q(year_end__gte=year_int) | models.Q(year_end__isnull=True)
            ).first()
            
            if brand_model_series and brand_model_series.series:
                series = brand_model_series.series
        
        # Find all matches that apply to our selection
        all_matches = Match.objects.all()
        matching_matches = []
        
        for match in all_matches:
            if match.matches_criteria(brand=brand, model=model, series=series, package=package, year=year_int):
                matching_matches.append(match)
        
        # If no matches found, return fallback content with message
        if not matching_matches:
            return JsonResponse({
                'success': True,
                'content': FALLBACK_CONTENT,
                'message': MESSAGES['no_matches_found'],
                'message_type': 'warning',
                'matches_found': 0,
                'selection_info': {
                    'brand': brand.name if brand else None,
                    'model': model.name if model else None,
                    'year': year_int,
                    'series': series.name if series else None,
                    'package': package.name if package else None,
                }
            })
        
        # Collect all MatchItems from matching matches, grouped by placement
        content_by_placement = {}
        for placement in ['interior', 'exterior', 'highlights', 'options']:
            content_by_placement[placement] = []
        
        for match in matching_matches:
            match_items = MatchItem.objects.filter(match=match).select_related('blurb', 'blurb__blurb_group')
            for item in match_items:
                content_by_placement[item.placement].append(item)
        
        # Generate content for each placement category
        generated_content = {}
        content_truncated = False
        
        for placement, items in content_by_placement.items():
            if not items:
                generated_content[placement] = ''
                continue
            
            # Apply BlurbGroup exclusion/replacement logic
            filtered_items = _apply_blurb_group_logic(items)
            
            # Sort by priority (descending) then sequence (ascending)
            sorted_items = sorted(filtered_items, key=lambda x: (-x.priority, x.sequence))
            
            # Build content string respecting character limits
            max_chars = CONTENT_LIMITS.get(placement, 500)
            content_parts = []
            current_length = 0
            
            for item in sorted_items:
                blurb_text = item.blurb.text.strip()
                
                # Check if adding this blurb would exceed the limit
                additional_length = len(blurb_text)
                if content_parts:  # Add separator length if not first item
                    additional_length += len(CONTENT_SEPARATOR)
                
                if current_length + additional_length + len(CONTENT_ENDING) <= max_chars:
                    content_parts.append(blurb_text)
                    current_length += additional_length
                else:
                    content_truncated = True
                    break
            
            # Join parts and add ending with proper dot handling
            if content_parts:
                # Process each part to ensure proper punctuation
                processed_parts = []
                for part in content_parts:
                    # Ensure each part ends with a dot if it doesn't already
                    if not part.endswith('.'):
                        part += '.'
                    processed_parts.append(part)
                
                # Join with space (not '. ') since parts already end with dots
                content = ' '.join(processed_parts)
            else:
                content = ''
            
            generated_content[placement] = content
        
        # Determine response message
        message = MESSAGES['content_generated']
        message_type = 'success'
        if content_truncated:
            message = MESSAGES['content_truncated']
            message_type = 'info'
        
        return JsonResponse({
            'success': True,
            'content': generated_content,
            'message': message,
            'message_type': message_type,
            'matches_found': len(matching_matches),
            'selection_info': {
                'brand': brand.name if brand else None,
                'model': model.name if model else None,
                'year': year_int,
                'series': series.name if series else None,
                'package': package.name if package else None,
            },
            'content_stats': {
                placement: {
                    'length': len(content),
                    'limit': CONTENT_LIMITS.get(placement, 500),
                    'items_used': len([item for item in content_by_placement[placement] 
                                     if item.blurb.text in content])
                }
                for placement, content in generated_content.items()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
