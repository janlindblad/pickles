from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Brand, Model, Series, Package, Year, BlurbGroup, Blurb, Match, MatchItem, BrandModelSeries


class PackageInline(admin.TabularInline):
    """Inline admin for packages in BrandModelSeries."""
    model = Package.brand_model_series.through
    extra = 1
    verbose_name = "Package"
    verbose_name_plural = "Available Packages"


class MatchItemInline(admin.TabularInline):
    """Inline admin for match items in Match."""
    model = MatchItem
    extra = 1
    fields = ['blurb', 'placement', 'is_highlight', 'is_option', 'priority', 'sequence']
    ordering = ['placement', 'sequence', '-priority']


class BlurbMatchItemInline(admin.TabularInline):
    """Inline admin to show match items that use this blurb."""
    model = MatchItem
    extra = 0
    fields = ['match', 'placement', 'is_highlight', 'is_option', 'priority', 'sequence']
    readonly_fields = ['match', 'placement', 'is_highlight', 'is_option', 'priority', 'sequence']
    ordering = ['placement', 'sequence', '-priority']
    verbose_name = "Match Item using this Blurb"
    verbose_name_plural = "Match Items using this Blurb"
    
    def has_add_permission(self, request, obj=None):
        # Don't allow adding new match items from the blurb admin
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deleting match items from the blurb admin  
        return False


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


@admin.register(Series)
class SeriesAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Series model with history tracking.
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


@admin.register(BlurbGroup)
class BlurbGroupAdmin(SimpleHistoryAdmin):
    """
    Admin interface for BlurbGroup model with history tracking.
    """
    list_display = ['name', 'max_items', 'get_blurb_count']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Group Settings', {
            'fields': ('max_items',),
            'description': 'Maximum items from this group allowed in content (1 = replacement logic)'
        }),
    )
    
    def get_blurb_count(self, obj):
        """Return the number of blurbs in this group."""
        return obj.blurbs.count()
    get_blurb_count.short_description = 'Blurbs in Group'
    get_blurb_count.admin_order_field = 'blurbs__count'


@admin.register(Blurb)
class BlurbAdmin(SimpleHistoryAdmin):
    """
    Admin interface for Blurb model with history tracking.
    """
    list_display = ['get_text_preview', 'get_match_count', 'get_match_info', 'blurb_group', 'group_priority', 'id']
    list_filter = ['blurb_group', 'match_items__placement']
    search_fields = ['text', 'blurb_group__name', 'match_items__match__brand__name', 'match_items__match__model__name']
    ordering = ['blurb_group__name', '-group_priority', 'id']
    inlines = [BlurbMatchItemInline]
    
    fieldsets = (
        ('Content', {
            'fields': ('text',)
        }),
        ('Group Settings', {
            'fields': ('blurb_group', 'group_priority'),
            'description': 'Optional group for exclusion/replacement logic. Higher priority wins within group.'
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset to reduce database queries."""
        queryset = super().get_queryset(request)
        return queryset.select_related('blurb_group').prefetch_related(
            'match_items__match__brand',
            'match_items__match__model', 
            'match_items__match__series',
            'match_items__match__package'
        )
    
    def get_text_preview(self, obj):
        """Return a preview of the blurb text for admin display."""
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    get_text_preview.short_description = 'Text Preview'
    
    def get_match_count(self, obj):
        """Return the number of match items that use this blurb."""
        count = obj.match_items.count()
        if count == 0:
            return "❌ No matches"
        return f"✅ {count} match{'es' if count != 1 else ''}"
    get_match_count.short_description = 'Usage'
    get_match_count.admin_order_field = 'match_items__count'
    
    def get_match_info(self, obj):
        """Return a summary of matches that use this blurb."""
        match_items = obj.match_items.select_related(
            'match__brand', 'match__model', 'match__series', 'match__package'
        ).all()[:3]  # Limit to first 3 to avoid long strings
        
        if not match_items:
            return "No usage"
        
        info_parts = []
        for item in match_items:
            match = item.match
            parts = []
            if match.brand:
                parts.append(match.brand.name)
            if match.model:
                parts.append(match.model.name)
            if match.package:
                parts.append(f"({match.package.name})")
            
            match_desc = " ".join(parts) if parts else "All vehicles"
            info_parts.append(f"{item.get_placement_display()}: {match_desc}")
        
        result = " | ".join(info_parts)
        if obj.match_items.count() > 3:
            result += f" (+{obj.match_items.count() - 3} more)"
        
        return result
    get_match_info.short_description = 'Used In'
    get_match_info.allow_tags = True


@admin.register(BrandModelSeries)
class BrandModelSeriesAdmin(SimpleHistoryAdmin):
    """
    Admin interface for BrandModelSeries model with history tracking.
    """
    list_display = ['brand', 'model', 'get_year_display', 'series', 'get_package_count']
    list_filter = ['brand', 'model', 'series', 'year_start']
    search_fields = ['brand__name', 'model__name', 'series__name']
    ordering = ['brand__name', 'model__name', '-year_start']
    inlines = [PackageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('brand', 'model', 'series')
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
    list_display = ['id', '__str__', 'get_item_count']
    list_filter = ['brand', 'model', 'series', 'year_start', 'year_end']
    search_fields = ['brand__name', 'model__name', 'series__name']
    ordering = ['id']
    inlines = [MatchItemInline]
    
    fieldsets = (
        ('Match Filters', {
            'fields': ('brand', 'model', 'series', 'package'),
            'description': 'Leave fields empty to match any value for that filter.'
        }),
        ('Year Range Filters', {
            'fields': ('year_start', 'year_end'),
            'description': 'Optional year range filters. Leave empty to match any year.'
        }),
    )
    
    def get_item_count(self, obj):
        """Return the number of match items for this match."""
        return obj.items.count()
    get_item_count.short_description = 'Items'
    get_item_count.admin_order_field = 'items__count'


@admin.register(MatchItem)
class MatchItemAdmin(SimpleHistoryAdmin):
    """
    Admin interface for MatchItem model with history tracking.
    """
    list_display = ['match', 'placement', 'is_highlight', 'is_option', 'priority', 'sequence', 'get_blurb_preview', 'get_categories_display']
    list_filter = ['placement', 'is_highlight', 'is_option', 'match__brand', 'match__model', 'match__series']
    search_fields = ['blurb__text', 'match__brand__name', 'match__model__name']
    ordering = ['match', 'placement', 'sequence', '-priority']
    
    fieldsets = (
        ('Content', {
            'fields': ('match', 'blurb')
        }),
        ('Placement & Categories', {
            'fields': ('placement', 'is_highlight', 'is_option'),
            'description': 'Placement: interior or exterior. Checkboxes: item will appear in highlights/options sections.'
        }),
        ('Priority & Sequence', {
            'fields': ('priority', 'sequence'),
            'description': 'Priority: higher numbers selected first. Sequence: lower numbers appear first.'
        }),
    )
    
    def get_blurb_preview(self, obj):
        """Return a preview of the blurb text."""
        return obj.blurb.text[:50] + "..." if len(obj.blurb.text) > 50 else obj.blurb.text
    get_blurb_preview.short_description = 'Blurb Preview'
    
    def get_categories_display(self, obj):
        """Display which categories this item appears in."""
        categories = obj.get_categories()
        return ', '.join(categories) if categories else '—'
    get_categories_display.short_description = 'Categories'
