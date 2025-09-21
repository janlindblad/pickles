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
import json

from .models import Brand, Model, Package, Year, Blurb, Match


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
    years = Year.objects.all().order_by('-name')  # Most recent first
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
    
    For now, returns all packages. Will be enhanced to filter based on
    the selected Brand, Model, and Year combination.
    
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
        
        # For now, return all packages regardless of selection
        # TODO: Add logic to filter packages based on Brand, Model, Year
        packages = Package.objects.all().order_by('name')
        
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
            'filter_applied': {
                'brand_id': brand_id,
                'model_id': model_id,
                'year_id': year_id,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
