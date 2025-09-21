"""
URL Configuration for the maker application.

This module defines URL patterns for the maker app, including the main
start page and API endpoints for dynamic content loading.
"""

from django.urls import path
from . import views

app_name = 'maker'

urlpatterns = [
    # Main start page
    path('', views.maker_start_view, name='start'),
    
    # API endpoints  
    path('api/packages/', views.maker_packages_api, name='packages_api'),
]