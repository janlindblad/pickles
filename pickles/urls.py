"""
URL configuration for pickles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('maker.urls')),  # Root URL points to maker app (includes /setup/)
    path('speeder/', include('speeder.urls')),  # Bulk management interface
]

# Customize admin site branding
admin.site.site_title = 'Pickles Admin'
admin.site.site_header = 'Pickles Administration'
admin.site.index_title = 'Welcome to Pickles Admin'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Note: Static files are served automatically by Django development server when DEBUG=True
# No additional configuration needed for app-level static files (maker/static/maker/)
