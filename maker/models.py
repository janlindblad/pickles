from django.db import models
from django.core.validators import MaxLengthValidator
from simple_history.models import HistoricalRecords
from .constants import BLURB_TEXT_MAX_LENGTH


class Brand(models.Model):
    """
    Represents a brand name for products.
    """
    name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Model(models.Model):
    """
    Represents a model name for products.
    """
    name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Series(models.Model):
    """
    Represents a series/generation name that can be shared across multiple BrandModelSeries.
    """
    name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Series"


class Package(models.Model):
    """
    Represents a package type for products.
    """
    name = models.CharField(max_length=100)
    brand_model_series = models.ManyToManyField('BrandModelSeries', related_name='packages')
    history = HistoricalRecords()
    
    def __str__(self):
        # Show associated brand/model/series context for clarity in admin
        series_list = list(self.brand_model_series.all()[:3])  # Limit to first 3 to avoid long strings
        if series_list:
            series_names = [str(series) for series in series_list]
            context = ' | '.join(series_names)
            if self.brand_model_series.count() > 3:
                context += f' (+{self.brand_model_series.count() - 3} more)'
            return f"{self.name} ({context})"
        else:
            return f"{self.name} (no series assigned)"
    
    class Meta:
        ordering = ['name']


class Year(models.Model):
    """
    Represents a year for products. Using integer for proper sorting and math operations.
    """
    year = models.IntegerField(unique=True, help_text="Four-digit year")
    history = HistoricalRecords()
    
    def __str__(self):
        return str(self.year)
    
    class Meta:
        ordering = ['-year']  # Most recent years first


class BlurbGroup(models.Model):
    """
    Represents a group of blurbs with exclusion/replacement logic.
    Used to ensure only one blurb from a group appears in generated content.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Description of what this group represents")
    max_items = models.IntegerField(default=1, help_text="Maximum items from this group allowed in content (1=replacement logic)")
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Blurb Group"
        verbose_name_plural = "Blurb Groups"


class Blurb(models.Model):
    """
    Represents marketing text/blurb content.
    Limited to 35 characters to ensure concise, effective messaging.
    """
    text = models.CharField(max_length=BLURB_TEXT_MAX_LENGTH, 
                           help_text=f"Marketing text (max {BLURB_TEXT_MAX_LENGTH} characters)")
    blurb_group = models.ForeignKey(BlurbGroup, null=True, blank=True, 
                                   on_delete=models.SET_NULL,
                                   related_name='blurbs',
                                   help_text="Blurb group for exclusion/replacement logic")
    group_priority = models.IntegerField(default=0, 
                                       help_text="Priority within blurb group (higher values win in replacement)")
    history = HistoricalRecords()
    
    def __str__(self):
        # Return first 50 characters of text for display
        return self.text[:50] + "..." if len(self.text) > 50 else self.text
    
    class Meta:
        ordering = ['id']


class BlurbInfo(models.Model):
    """
    Represents back office photos/drawings and info texts associated with blurbs.
    Only displayed for items in the options column, providing detailed technical information.
    """
    blurb = models.ForeignKey(Blurb, on_delete=models.CASCADE, related_name='blurb_info')
    image = models.ImageField(upload_to='blurb_info/', help_text="Photo or drawing for back office reference")
    info_text = models.TextField(blank=True, help_text="Technical details or additional information")
    sequence = models.IntegerField(default=0, help_text="Display order for multiple images (lower numbers appear first)")
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"Info for {self.blurb} - {self.image.name}"
    
    class Meta:
        ordering = ['sequence', 'created_at']
        verbose_name = "Blurb Info"
        verbose_name_plural = "Blurb Info"


class BrandModelSeries(models.Model):
    """
    Represents a series/generation of a Brand+Model with shared packages.
    Groups years that have the same package availability for efficient storage.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='model_series')
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='brand_series')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='brand_model_series', null=True, blank=True, help_text="Optional series/generation")
    year_start = models.IntegerField(help_text="First year this series was available")
    year_end = models.IntegerField(null=True, blank=True, help_text="Last year (leave empty if ongoing)")
    history = HistoricalRecords()
    
    def get_year_display(self):
        """Return a human-readable year range string."""
        if self.year_end and self.year_end != self.year_start:
            return f"{self.year_start}-{self.year_end}"
        elif self.year_end:
            return str(self.year_start)
        else:
            return f"{self.year_start}+"
    
    def is_year_available(self, year_int):
        """Check if a specific year is covered by this series."""
        if self.year_end:
            return self.year_start <= year_int <= self.year_end
        else:
            return year_int >= self.year_start
    
    def get_available_years(self):
        """Return queryset of Year objects covered by this series."""
        if self.year_end:
            return Year.objects.filter(year__gte=self.year_start, year__lte=self.year_end)
        else:
            return Year.objects.filter(year__gte=self.year_start)
    
    def __str__(self):
        series = f" {self.series.name}" if self.series else ""
        return f"{self.brand.name} {self.model.name} ({self.get_year_display()}){series}"
    
    class Meta:
        unique_together = ['brand', 'model', 'year_start']
        ordering = ['brand__name', 'model__name', '-year_start']
        verbose_name_plural = "Brand Model Series"


class Match(models.Model):
    """
    Represents matching conditions that trigger content generation.
    When conditions are met, associated MatchItems are selected for content.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='matches', null=True, blank=True, help_text="Optional brand filter")
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='matches', null=True, blank=True, help_text="Optional model filter")
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='matches', null=True, blank=True, help_text="Optional series filter")
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='matches', null=True, blank=True, help_text="Optional package filter")
    year_start = models.IntegerField(null=True, blank=True, help_text="Optional earliest model year")
    year_end = models.IntegerField(null=True, blank=True, help_text="Optional latest model year")
    history = HistoricalRecords()
    
    def matches_criteria(self, brand=None, model=None, series=None, package=None, year=None):
        """
        Check if this Match applies to the given criteria.
        Returns True if all specified filters match the given values.
        """
        if self.brand and brand != self.brand:
            return False
        if self.model and model != self.model:
            return False
        if self.series and series != self.series:
            return False
        if self.package and package != self.package:
            return False
        if year:
            if self.year_start and year < self.year_start:
                return False
            if self.year_end and year > self.year_end:
                return False
        return True
    
    def __str__(self):
        filters = []
        if self.brand:
            filters.append(f"Brand: {self.brand.name}")
        if self.model:
            filters.append(f"Model: {self.model.name}")
        if self.series:
            filters.append(f"Series: {self.series.name}")
        if self.package:
            filters.append(f"Package: {self.package.name}")
        if self.year_start or self.year_end:
            if self.year_start and self.year_end:
                filters.append(f"Years: {self.year_start}-{self.year_end}")
            elif self.year_start:
                filters.append(f"Years: {self.year_start}+")
            elif self.year_end:
                filters.append(f"Years: -{self.year_end}")
        
        if filters:
            return f"Match ({', '.join(filters)})"
        else:
            return "Match (no filters)"
    
    class Meta:
        ordering = ['id']
        verbose_name_plural = "Matches"


class MatchItem(models.Model):
    """
    Represents a content item that can be selected when a Match triggers.
    Items have primary placement (interior/exterior) and can also be marked as highlights and/or options.
    This allows items to appear in multiple content categories simultaneously.
    """
    PLACEMENT_CHOICES = [
        ('interior', 'Interior'),
        ('exterior', 'Exterior'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='items')
    blurb = models.ForeignKey(Blurb, on_delete=models.CASCADE, related_name='match_items')
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, 
                                help_text="Primary content category (Interior or Exterior)")
    is_highlight = models.BooleanField(default=False, 
                                     help_text="Check to also show this item in Highlights")
    is_option = models.BooleanField(default=False, 
                                  help_text="Check to also show this item in Options")
    sequence = models.IntegerField(default=0, help_text="Display order within category (lower numbers appear first)")
    history = HistoricalRecords()
    
    def get_categories(self):
        """Return list of categories this item appears in."""
        categories = [self.placement]
        if self.is_highlight:
            categories.append('highlights')
        if self.is_option:
            categories.append('options')
        return categories
    
    def __str__(self):
        categories = ', '.join([cat.title() for cat in self.get_categories()])
        return f"{categories} - {self.blurb}"
    
    class Meta:
        ordering = ['placement', 'sequence']
        verbose_name = "Match Item"
        verbose_name_plural = "Match Items"
