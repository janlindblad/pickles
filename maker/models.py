from django.db import models
from simple_history.models import HistoricalRecords


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


class Blurb(models.Model):
    """
    Represents marketing text/blurb content.
    """
    text = models.TextField()
    history = HistoricalRecords()
    
    def __str__(self):
        # Return first 50 characters of text for display
        return self.text[:50] + "..." if len(self.text) > 50 else self.text
    
    class Meta:
        ordering = ['id']


class BrandModelSeries(models.Model):
    """
    Represents a series/generation of a Brand+Model with shared packages.
    Groups years that have the same package availability for efficient storage.
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='model_series')
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='brand_series')
    series_name = models.CharField(max_length=100, blank=True, help_text="Optional series/generation name")
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
        series = f" {self.series_name}" if self.series_name else ""
        return f"{self.brand.name} {self.model.name} ({self.get_year_display()}){series}"
    
    class Meta:
        unique_together = ['brand', 'model', 'year_start']
        ordering = ['brand__name', 'model__name', '-year_start']
        verbose_name_plural = "Brand Model Series"


class Match(models.Model):
    """
    Represents a match between a blurb and other entities.
    This model will be expanded with more relationships in the future.
    """
    blurb = models.ForeignKey(Blurb, on_delete=models.CASCADE, related_name='matches')
    history = HistoricalRecords()
    
    def __str__(self):
        return f"Match for: {self.blurb}"
    
    class Meta:
        ordering = ['id']
