"""
Speeder App Views

This module contains views for the bulk data management interface.
It provides a streamlined interface for managing large amounts of 
brand, model, series, and blurb data.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
import json

from maker.models import Brand, Model, Series, Package, Blurb, Match, MatchItem, BrandModelSeries


def is_staff_user(user):
    """Check if user is staff (admin)."""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff_user, login_url='/admin/login/')
def speeder_index(request):
    """
    Main speeder interface view.
    Provides the bulk data management interface for admin users.
    """
    context = {
        'page_title': 'Speeder - Bulk Data Management'
    }
    return render(request, 'speeder/index.html', context)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def brands_api(request):
    """
    API endpoint to get all brands for the brand selection cards.
    """
    try:
        brands = Brand.objects.all().order_by('name')
        brands_data = [
            {
                'id': brand.id,
                'name': brand.name,
            }
            for brand in brands
        ]
        
        return JsonResponse({
            'success': True,
            'brands': brands_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def models_api(request, brand_id):
    """
    API endpoint to get all models for a specific brand.
    """
    try:
        brand = Brand.objects.get(id=brand_id)
        models = Model.objects.filter(brand_series__brand=brand).distinct().order_by('name')
        
        models_data = [
            {
                'id': model.id,
                'name': model.name,
            }
            for model in models
        ]
        
        return JsonResponse({
            'success': True,
            'brand': {'id': brand.id, 'name': brand.name},
            'models': models_data
        })
        
    except Brand.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Brand with id {brand_id} not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def series_api(request, brand_id, model_id):
    """
    API endpoint to get all series for a specific brand and model.
    """
    try:
        brand = Brand.objects.get(id=brand_id)
        model = Model.objects.get(id=model_id)
        
        brand_model_series = BrandModelSeries.objects.filter(
            brand=brand, 
            model=model
        ).select_related('series').order_by('series__name', '-year_start')
        
        series_data = [
            {
                'id': bms.series.id if bms.series else None,
                'name': bms.series.name if bms.series else 'No Series',
                'year_range': bms.get_year_display(),
                'brand_model_series_id': bms.id,
            }
            for bms in brand_model_series
        ]
        
        return JsonResponse({
            'success': True,
            'brand': {'id': brand.id, 'name': brand.name},
            'model': {'id': model.id, 'name': model.name},
            'series': series_data
        })
        
    except (Brand.DoesNotExist, Model.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Brand or Model not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def blurbs_api(request, brand_id, model_id, series_id):
    """
    API endpoint to get blurb management data for a specific brand, model, and series.
    Returns packages and existing blurbs with their package associations.
    """
    try:
        brand = Brand.objects.get(id=brand_id)
        model = Model.objects.get(id=model_id)
        
        if series_id == 0:  # Handle "No Series" case
            series = None
        else:
            series = Series.objects.get(id=series_id)
        
        # Get all packages for this brand/model combination
        brand_model_series = BrandModelSeries.objects.filter(
            brand=brand, 
            model=model,
            series=series
        ).first()
        
        if not brand_model_series:
            return JsonResponse({
                'success': False,
                'error': 'No BrandModelSeries found for this combination'
            }, status=404)
        
        packages = brand_model_series.packages.all().order_by('name')
        
        # Get all matches for this brand/model/series combination
        matches = Match.objects.filter(
            brand=brand,
            model=model,
            series=series
        ).prefetch_related('items__blurb')
        
        # Organize match items by blurb and package
        blurb_package_map = {}  # blurb_id -> {package_id: match_item, ...}
        all_blurbs = set()
        
        for match in matches:
            for match_item in match.items.all():
                blurb_id = match_item.blurb.id
                package_id = match.package.id if match.package else None
                
                if blurb_id not in blurb_package_map:
                    blurb_package_map[blurb_id] = {}
                
                blurb_package_map[blurb_id][package_id] = match_item
                all_blurbs.add(match_item.blurb)
        
        # Format response data
        packages_data = [
            {
                'id': package.id,
                'name': package.name,
            }
            for package in packages
        ]
        
        # Add "All Packages" (null package) column
        packages_data.insert(0, {
            'id': None,
            'name': 'All Packages',
        })
        
        blurbs_data = []
        for blurb in sorted(all_blurbs, key=lambda b: b.id):
            package_associations = blurb_package_map.get(blurb.id, {})
            
            # Build package checkbox states
            package_states = {}
            for package_data in packages_data:
                package_id = package_data['id']
                match_item = package_associations.get(package_id)
                
                if match_item:
                    package_states[str(package_id) if package_id else 'null'] = {
                        'checked': True,
                        'placement': match_item.placement,
                        'is_highlight': match_item.is_highlight,
                        'is_option': match_item.is_option,
                        'sequence': match_item.sequence,
                        'match_item_id': match_item.id,
                        'is_complex': match_item.is_complex,
                    }
                else:
                    package_states[str(package_id) if package_id else 'null'] = {
                        'checked': False,
                        'placement': 'interior',  # default
                        'is_highlight': False,
                        'is_option': False,
                        'sequence': 0,
                        'match_item_id': None,
                        'is_complex': False,  # Default state is not complex
                    }
            
            blurbs_data.append({
                'id': blurb.id,
                'text': blurb.text,
                'package_states': package_states,
            })
        
        return JsonResponse({
            'success': True,
            'brand': {'id': brand.id, 'name': brand.name},
            'model': {'id': model.id, 'name': model.name},
            'series': {'id': series.id, 'name': series.name} if series else {'id': None, 'name': 'No Series'},
            'packages': packages_data,
            'blurbs': blurbs_data,
            'brand_model_series_id': brand_model_series.id,
        })
        
    except (Brand.DoesNotExist, Model.DoesNotExist, Series.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Brand, Model, or Series not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def blurbs_search_api(request):
    """
    API endpoint to search for existing blurbs by text query.
    Used for autocomplete functionality when adding new blurbs.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({
                'success': True,
                'blurbs': []
            })
        
        # Search for blurbs containing the query (case-insensitive)
        # Limit to prevent overwhelming the UI
        blurbs = Blurb.objects.filter(
            text__icontains=query
        ).select_related('blurb_group')[:20]  # Limit to 20 results
        
        blurbs_data = [
            {
                'id': blurb.id,
                'text': blurb.text,
            }
            for blurb in blurbs
        ]
        
        return JsonResponse({
            'success': True,
            'blurbs': blurbs_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def packages_api(request, brand_id, model_id, series_id):
    """
    API endpoint to get packages for a specific brand/model/series combination.
    """
    try:
        brand = Brand.objects.get(id=brand_id)
        model = Model.objects.get(id=model_id)
        
        if series_id == 0:  # Handle "No Series" case
            series = None
        else:
            series = Series.objects.get(id=series_id)
        
        # Get BrandModelSeries
        brand_model_series = BrandModelSeries.objects.filter(
            brand=brand, 
            model=model,
            series=series
        ).first()
        
        if not brand_model_series:
            return JsonResponse({
                'success': False,
                'error': 'No BrandModelSeries found for this combination'
            }, status=404)
        
        # Get associated packages
        packages = brand_model_series.packages.all().order_by('name')
        
        packages_data = [
            {
                'id': package.id,
                'name': package.name,
            }
            for package in packages
        ]
        
        return JsonResponse({
            'success': True,
            'brand': {'id': brand.id, 'name': brand.name},
            'model': {'id': model.id, 'name': model.name},
            'series': {'id': series.id, 'name': series.name} if series else {'id': None, 'name': 'No Series'},
            'packages': packages_data,
            'brand_model_series_id': brand_model_series.id,
        })
        
    except (Brand.DoesNotExist, Model.DoesNotExist, Series.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Brand, Model, or Series not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def packages_search_api(request):
    """
    API endpoint to search for existing packages by name.
    Used for autocomplete when adding packages.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return JsonResponse({
                'success': True,
                'packages': []
            })
        
        # Search for packages containing the query (case-insensitive)
        packages = Package.objects.filter(
            name__icontains=query
        )[:20]  # Limit to 20 results
        
        packages_data = [
            {
                'id': package.id,
                'name': package.name,
            }
            for package in packages
        ]
        
        return JsonResponse({
            'success': True,
            'packages': packages_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def create_package_api(request):
    """
    API endpoint to create a new package and associate it with a BrandModelSeries.
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        brand_model_series_id = data.get('brand_model_series_id')
        
        if not name:
            return JsonResponse({
                'success': False,
                'error': 'Package name is required'
            }, status=400)
        
        # Check if package with this name already exists
        existing_package = Package.objects.filter(name__iexact=name).first()
        if existing_package:
            return JsonResponse({
                'success': False,
                'error': f'Package with name "{name}" already exists'
            }, status=400)
        
        # Get BrandModelSeries
        brand_model_series = BrandModelSeries.objects.get(id=brand_model_series_id)
        
        # Create new package
        package = Package.objects.create(name=name)
        brand_model_series.packages.add(package)
        
        return JsonResponse({
            'success': True,
            'package': {
                'id': package.id,
                'name': package.name,
            }
        })
        
    except BrandModelSeries.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'BrandModelSeries not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def add_package_to_series_api(request):
    """
    API endpoint to associate an existing package with a BrandModelSeries.
    """
    try:
        data = json.loads(request.body)
        package_id = data.get('package_id')
        brand_model_series_id = data.get('brand_model_series_id')
        
        # Get objects
        package = Package.objects.get(id=package_id)
        brand_model_series = BrandModelSeries.objects.get(id=brand_model_series_id)
        
        # Check if already associated
        if brand_model_series.packages.filter(id=package_id).exists():
            return JsonResponse({
                'success': False,
                'error': f'Package "{package.name}" is already associated with this series'
            }, status=400)
        
        # Associate package
        brand_model_series.packages.add(package)
        
        return JsonResponse({
            'success': True,
            'package': {
                'id': package.id,
                'name': package.name,
            }
        })
        
    except (Package.DoesNotExist, BrandModelSeries.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Package or BrandModelSeries not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def remove_package_from_series_api(request):
    """
    API endpoint to remove a package association from a BrandModelSeries.
    """
    try:
        data = json.loads(request.body)
        package_id = data.get('package_id')
        brand_model_series_id = data.get('brand_model_series_id')
        
        # Get objects
        package = Package.objects.get(id=package_id)
        brand_model_series = BrandModelSeries.objects.get(id=brand_model_series_id)
        
        # Check if associated
        if not brand_model_series.packages.filter(id=package_id).exists():
            return JsonResponse({
                'success': False,
                'error': f'Package "{package.name}" is not associated with this series'
            }, status=400)
        
        # Remove association
        brand_model_series.packages.remove(package)
        
        return JsonResponse({
            'success': True
        })
        
    except (Package.DoesNotExist, BrandModelSeries.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Package or BrandModelSeries not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def save_blurb_packages(request):
    """
    API endpoint to save blurb package associations.
    Creates/updates/deletes Match and MatchItem objects as needed.
    """
    try:
        data = json.loads(request.body)
        blurb_id = data.get('blurb_id')
        brand_id = data.get('brand_id')
        model_id = data.get('model_id')
        series_id = data.get('series_id')
        package_states = data.get('package_states', {})
        
        with transaction.atomic():
            # Get objects
            blurb = Blurb.objects.get(id=blurb_id)
            brand = Brand.objects.get(id=brand_id)
            model = Model.objects.get(id=model_id)
            series = Series.objects.get(id=series_id) if series_id else None
            
            # Process each package state
            for package_key, state in package_states.items():
                package_id = None if package_key == 'null' else int(package_key)
                package = Package.objects.get(id=package_id) if package_id else None
                
                # Find or create match for this package
                match, created = Match.objects.get_or_create(
                    brand=brand,
                    model=model,
                    series=series,
                    package=package,
                    defaults={
                        'year_start': None,
                        'year_end': None,
                    }
                )
                
                # Find existing match item for this blurb in this match
                existing_match_item = MatchItem.objects.filter(
                    match=match,
                    blurb=blurb
                ).first()
                
                if state['checked']:
                    # Create or update match item
                    if existing_match_item:
                        existing_match_item.placement = state['placement']
                        existing_match_item.is_highlight = state['is_highlight']
                        existing_match_item.is_option = state['is_option']
                        existing_match_item.sequence = state['sequence']
                        existing_match_item.save()
                    else:
                        MatchItem.objects.create(
                            match=match,
                            blurb=blurb,
                            placement=state['placement'],
                            is_highlight=state['is_highlight'],
                            is_option=state['is_option'],
                            sequence=state['sequence']
                        )
                else:
                    # Delete match item if it exists
                    if existing_match_item:
                        existing_match_item.delete()
                
                # Clean up empty matches
                if not match.items.exists():
                    match.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Blurb package associations saved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def create_brand(request):
    """
    API endpoint to create a new brand.
    """
    try:
        data = json.loads(request.body)
        brand_name = data.get('name', '').strip()
        
        if not brand_name:
            return JsonResponse({
                'success': False,
                'error': 'Brand name is required'
            }, status=400)
        
        brand = Brand.objects.create(name=brand_name)
        
        return JsonResponse({
            'success': True,
            'brand': {
                'id': brand.id,
                'name': brand.name,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def create_model(request):
    """
    API endpoint to create a new model.
    If a brand_id is provided, also creates a BrandModelSeries entry.
    """
    try:
        data = json.loads(request.body)
        model_name = data.get('name', '').strip()
        brand_id = data.get('brand_id')  # Optional brand association
        
        if not model_name:
            return JsonResponse({
                'success': False,
                'error': 'Model name is required'
            }, status=400)
        
        with transaction.atomic():
            # Create the model
            model = Model.objects.create(name=model_name)
            
            # If brand_id provided, create BrandModelSeries
            if brand_id:
                try:
                    brand = Brand.objects.get(id=brand_id)
                    # Create BrandModelSeries with placeholder year (will be updated when series created)
                    BrandModelSeries.objects.create(
                        brand=brand,
                        model=model,
                        series=None,  # No series yet
                        year_start=2024,  # Default placeholder year
                        year_end=None,
                    )
                except Brand.DoesNotExist:
                    # Brand doesn't exist, but don't fail the model creation
                    pass
        
        return JsonResponse({
            'success': True,
            'model': {
                'id': model.id,
                'name': model.name,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def create_series(request):
    """
    API endpoint to create a new series with BrandModelSeries entry.
    """
    try:
        data = json.loads(request.body)
        series_name = data.get('name', '').strip()
        brand_id = data.get('brand_id')
        model_id = data.get('model_id')
        year_start = data.get('year_start')
        year_end = data.get('year_end')
        
        if not series_name:
            return JsonResponse({
                'success': False,
                'error': 'Series name is required'
            }, status=400)
        
        if not brand_id or not model_id:
            return JsonResponse({
                'success': False,
                'error': 'Brand and model IDs are required'
            }, status=400)
        
        if year_start is None:
            return JsonResponse({
                'success': False,
                'error': 'Year start is required'
            }, status=400)
        
        with transaction.atomic():
            # Create the series
            series = Series.objects.create(name=series_name)
            
            # Create BrandModelSeries entry
            brand = Brand.objects.get(id=brand_id)
            model = Model.objects.get(id=model_id)
            
            brand_model_series = BrandModelSeries.objects.create(
                brand=brand,
                model=model,
                series=series,
                year_start=year_start if year_start else None,
                year_end=year_end if year_end else None,
            )
        
        return JsonResponse({
            'success': True,
            'series': {
                'id': series.id,
                'name': series.name,
                'year_range': brand_model_series.get_year_display(),
                'brand_model_series_id': brand_model_series.id,
            }
        })
        
    except (Brand.DoesNotExist, Model.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Brand or Model not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@user_passes_test(is_staff_user, login_url='/admin/login/')
def create_blurb(request):
    """
    API endpoint to create a new blurb.
    """
    try:
        data = json.loads(request.body)
        blurb_text = data.get('text', '').strip()
        
        if not blurb_text:
            return JsonResponse({
                'success': False,
                'error': 'Blurb text is required'
            }, status=400)
        
        blurb = Blurb.objects.create(text=blurb_text)
        
        return JsonResponse({
            'success': True,
            'blurb': {
                'id': blurb.id,
                'text': blurb.text,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
