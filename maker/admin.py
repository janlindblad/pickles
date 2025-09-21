from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Brand, Model, Package, Year, Blurb, Match, BrandModelSeries


class PackageInline(admin.TabularInline):
    """Inline admin for packages in BrandModelSeries."""
    model = Package.brand_model_series.through
    extra = 1
    verbose_name = "Package"
    verbose_name_plural = "Available Packages"


@admin.register(Brand)
class BrandAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Brand model with history tracking.
    """
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Model)
class ModelAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Model model with history tracking.
    """
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Package)
class PackageAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Package model with history tracking.
    """
    list_display = ['get_package_with_context', 'get_series_count']
    search_fields = ['name', 'brand_model_series__brand__name', 'brand_model_series__model__name']
    list_filter = ['brand_model_series__brand', 'brand_model_series__model', 'name']
    ordering = ['name']
    filter_horizontal = ['brand_model_series']  # Nice interface for ManyToMany
    list_select_related = True
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch_related to avoid N+1 queries."""
        return super().get_queryset(request).prefetch_related(
            'brand_model_series__brand',
            'brand_model_series__model'
        )
    
    def get_package_with_context(self, obj):
        """Return package name with brand/model/series context."""
        return str(obj)  # This will use the enhanced __str__ method
    get_package_with_context.short_description = 'Package'
    get_package_with_context.admin_order_field = 'name'
    
    def get_series_count(self, obj):
        """Return the number of brand/model series this package is associated with."""
        return obj.brand_model_series.count()
    get_series_count.short_description = 'Series Count'


@admin.register(Year)
class YearAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Year model with history tracking.
    """
    list_display = ['year']
    search_fields = ['year']
    ordering = ['-year']  # Most recent years first


@admin.register(Blurb)
class BlurbAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Blurb model with history tracking.
    """
    list_display = ['get_text_preview', 'id']
    search_fields = ['text']
    ordering = ['id']
    
    def get_text_preview(self, obj):
        """Return a preview of the blurb text for admin display."""
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    get_text_preview.short_description = 'Text Preview'


@admin.register(BrandModelSeries)
class BrandModelSeriesAdmin(SimpleHistoryAdmin):
    """
    Admin interface for BrandModelSeries model with history tracking.
    """
    list_display = ['brand', 'model', 'get_year_display', 'series_name', 'get_package_count']
    list_filter = ['brand', 'model', 'year_start']
    search_fields = ['brand__name', 'model__name', 'series_name']
    ordering = ['brand__name', 'model__name', '-year_start']
    inlines = [PackageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'model', 'series_name')
        }),
        ('Year Range', {
            'fields': ('year_start', 'year_end'),
            'description': 'Leave "Year end" empty if this series is ongoing.'
        }),
    )
    
    def get_package_count(self, obj):
        """Return the number of packages associated with this series."""
        return obj.packages.count()
    get_package_count.short_description = 'Package Count'
    get_package_count.admin_order_field = 'packages__count'


@admin.register(Match)
class MatchAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Match model with history tracking.
    """
    list_display = ['id', 'get_blurb_preview']
    list_filter = ['blurb']
    ordering = ['id']
    
    def get_blurb_preview(self, obj):
        """Return a preview of the associated blurb text."""
        return obj.blurb.text[:50] + "..." if len(obj.blurb.text) > 50 else obj.blurb.text
    get_blurb_preview.short_description = 'Blurb Preview'
