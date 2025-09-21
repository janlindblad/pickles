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

from .models import Brand, Model, Package, Year, Blurb, Match, BrandModelSeries


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
