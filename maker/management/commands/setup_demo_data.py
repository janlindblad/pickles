"""
Django management command to set up demo data for the Pickles Maker application.

This command provides a user-friendly way to load demo data with options for
clearing existing data and showing progress.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import transaction
from django.utils.termcolors import make_style
from maker.models import (
    Brand, Model, Series, Package, Year, BlurbGroup, Blurb, 
    BrandModelSeries, Match, MatchItem
)
import os


class Command(BaseCommand):
    """
    Management command to set up demo data for development and testing.
    
    Usage:
        python manage.py setup_demo_data
        python manage.py setup_demo_data --clear
        python manage.py setup_demo_data --show-summary
    """
    
    help = 'Set up demo data for the Pickles Maker application'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_style = make_style(opts=('bold',), fg='green')
        self.warning_style = make_style(opts=('bold',), fg='yellow')
        self.error_style = make_style(opts=('bold',), fg='red')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing data before loading demo data'
        )
        
        parser.add_argument(
            '--show-summary',
            action='store_true',
            help='Show summary of demo data after loading'
        )
        
        parser.add_argument(
            '--fixture',
            type=str,
            default='demo_data_clean.json',
            help='Fixture file to load (default: demo_data_clean.json)'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        self.stdout.write(
            self.success_style('🚀 Pickles Maker Demo Data Setup')
        )
        self.stdout.write('=' * 50)
        
        # Check if fixture file exists
        fixture_path = os.path.join('maker', 'fixtures', options['fixture'])
        if not os.path.exists(fixture_path):
            raise CommandError(
                f"Fixture file {fixture_path} not found. "
                f"Make sure you have demo data fixtures available."
            )
        
        # Show current data status
        self._show_current_status()
        
        # Clear existing data if requested
        if options['clear']:
            self._clear_existing_data()
        
        # Load demo data
        self._load_demo_data(options['fixture'])
        
        # Show summary if requested
        if options['show_summary']:
            self._show_data_summary()
        
        self.stdout.write(
            self.success_style('\n✅ Demo data setup completed successfully!')
        )
        self.stdout.write('You can now explore the application with sample content.')
    
    def _show_current_status(self):
        """Display current database status."""
        self.stdout.write('\n📊 Current Database Status:')
        self.stdout.write('-' * 30)
        
        models_info = [
            ('Brands', Brand.objects.count()),
            ('Models', Model.objects.count()),
            ('Series', Series.objects.count()),
            ('Packages', Package.objects.count()),
            ('Years', Year.objects.count()),
            ('Blurb Groups', BlurbGroup.objects.count()),
            ('Blurbs', Blurb.objects.count()),
            ('Brand Model Series', BrandModelSeries.objects.count()),
            ('Matches', Match.objects.count()),
            ('Match Items', MatchItem.objects.count()),
        ]
        
        for name, count in models_info:
            if count > 0:
                self.stdout.write(f'  {name}: {self.success_style(str(count))}')
            else:
                self.stdout.write(f'  {name}: {count}')
    
    def _clear_existing_data(self):
        """Clear all existing maker app data."""
        self.stdout.write(f'\n{self.warning_style("⚠️  Clearing existing data...")}')
        
        with transaction.atomic():
            # Delete in reverse dependency order
            MatchItem.objects.all().delete()
            Match.objects.all().delete()
            # Don't delete Package.brand_model_series relationships directly
            # They'll be cleaned up when we delete BrandModelSeries
            BrandModelSeries.objects.all().delete()
            Blurb.objects.all().delete()
            BlurbGroup.objects.all().delete()
            Package.objects.all().delete()
            Year.objects.all().delete()
            Series.objects.all().delete()
            Model.objects.all().delete()
            Brand.objects.all().delete()
        
        self.stdout.write('  ✅ All existing data cleared')
    
    def _load_demo_data(self, fixture_name):
        """Load demo data from fixture."""
        self.stdout.write('\n📥 Loading demo data...')
        
        try:
            # Use Django's loaddata command
            call_command('loaddata', f'maker/fixtures/{fixture_name}', verbosity=0)
            self.stdout.write('  ✅ Demo data loaded successfully')
            
        except Exception as e:
            raise CommandError(f'Failed to load demo data: {e}')
    
    def _show_data_summary(self):
        """Show summary of loaded data."""
        self.stdout.write('\n📋 Demo Data Summary:')
        self.stdout.write('-' * 40)
        
        # Show brands and their models
        self.stdout.write('\n🏢 Brands and Models:')
        for brand in Brand.objects.all().order_by('name'):
            models = Model.objects.filter(brand_series__brand=brand).distinct()
            model_names = [m.name for m in models[:3]]
            if models.count() > 3:
                model_names.append(f'(+{models.count() - 3} more)')
            self.stdout.write(f'  • {brand.name}: {", ".join(model_names)}')
        
        # Show blurb groups
        if BlurbGroup.objects.exists():
            self.stdout.write('\n🏷️  Blurb Groups:')
            for group in BlurbGroup.objects.all():
                blurb_count = group.blurbs.count()
                self.stdout.write(f'  • {group.name}: {blurb_count} blurbs (max {group.max_items} per content)')
        
        # Show match statistics
        total_matches = Match.objects.count()
        total_items = MatchItem.objects.count()
        self.stdout.write(f'\n🎯 Content Rules: {total_matches} matches with {total_items} items')
        
        # Show placement distribution
        from django.db.models import Count
        placements = MatchItem.objects.values('placement').annotate(count=Count('id')).order_by('-count')
        if placements:
            self.stdout.write('   Placement distribution:')
            for p in placements:
                self.stdout.write(f'     - {p["placement"].title()}: {p["count"]} items')
        
        self.stdout.write('\n💡 Tips:')
        self.stdout.write('  • Visit /admin/ to explore and modify the demo data')
        self.stdout.write('  • Use the main application to generate content')
        self.stdout.write('  • Check out BlurbGroups for content exclusion examples')