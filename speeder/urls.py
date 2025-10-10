from django.urls import path
from . import views

app_name = 'speeder'

urlpatterns = [
    path('', views.speeder_index, name='index'),
    path('api/brands/', views.brands_api, name='brands_api'),
    path('api/models/<int:brand_id>/', views.models_api, name='models_api'),
    path('api/series/<int:brand_id>/<int:model_id>/', views.series_api, name='series_api'),
    path('api/blurbs/<int:brand_id>/<int:model_id>/<int:series_id>/', views.blurbs_api, name='blurbs_api'),
    path('api/blurbs/search/', views.blurbs_search_api, name='blurbs_search_api'),
    path('api/packages/<int:brand_id>/<int:model_id>/<int:series_id>/', views.packages_api, name='packages_api'),
    path('api/packages/search/', views.packages_search_api, name='packages_search_api'),
    path('api/create-package/', views.create_package_api, name='create_package_api'),
    path('api/add-package-to-series/', views.add_package_to_series_api, name='add_package_to_series_api'),
    path('api/remove-package-from-series/', views.remove_package_from_series_api, name='remove_package_from_series_api'),
    path('api/save-blurb-packages/', views.save_blurb_packages, name='save_blurb_packages'),
    path('api/create-blurb/', views.create_blurb, name='create_blurb'),
    path('api/create-brand/', views.create_brand, name='create_brand'),
    path('api/create-model/', views.create_model, name='create_model'),
    path('api/create-series/', views.create_series, name='create_series'),
]