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
    name = models.CharField(max_length=100, unique=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Year(models.Model):
    """
    Represents a year for products. Stored as string for flexibility.
    """
    name = models.CharField(max_length=4, unique=True, help_text="Four-digit year")
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-name']  # Most recent years first


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
