from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Brand, Model, Package, Year, Blurb, Match


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
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Year)
class YearAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Year model with history tracking.
    """
    list_display = ['name']
    search_fields = ['name']
    ordering = ['-name']  # Most recent years first


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
