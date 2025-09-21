"""
Django management command to backup and restore maker app data.

This provides database-agnostic backup and restore functionality using
Django's serialization system, with additional features like compression
and metadata.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from django.db import transaction
from django.utils.termcolors import make_style
from django.conf import settings
from maker.models import (
    Brand, Model, Series, Package, Year, BlurbGroup, Blurb, 
    BrandModelSeries, Match, MatchItem
)
import os
import json
import gzip
from datetime import datetime


class Command(BaseCommand):
    """
    Management command to backup and restore maker app data.
    
    Usage:
        python manage.py backup_restore --backup
        python manage.py backup_restore --restore backup_20250921_1557.json.gz
        python manage.py backup_restore --list-backups
    """
    
    help = 'Backup and restore maker app data'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_style = make_style(opts=('bold',), fg='green')
        self.warning_style = make_style(opts=('bold',), fg='yellow')
        self.error_style = make_style(opts=('bold',), fg='red')
        self.backup_dir = os.path.join(os.getcwd(), 'backups')
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a backup of current data'
        )
        
        parser.add_argument(
            '--restore',
            type=str,
            help='Restore data from backup file'
        )
        
        parser.add_argument(
            '--list-backups',
            action='store_true',
            help='List available backup files'
        )
        
        parser.add_argument(
            '--compress',
            action='store_true',
            default=True,
            help='Compress backup files (default: True)'
        )
        
        parser.add_argument(
            '--clear-before-restore',
            action='store_true',
            help='Clear existing data before restoring'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        if options['backup']:
            self._create_backup(options['compress'])
        elif options['restore']:
            self._restore_backup(options['restore'], options['clear_before_restore'])
        elif options['list_backups']:
            self._list_backups()
        else:
            self.stdout.write(
                self.error_style('Please specify --backup, --restore, or --list-backups')
            )
            return
    
    def _create_backup(self, compress=True):
        """Create a backup of current data."""
        self.stdout.write(
            self.success_style('🗄️  Creating backup of maker data...')
        )
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        if compress:
            filename += '.gz'
        
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # Get all objects to backup
            all_objects = self._get_all_objects()
            
            # Create metadata
            metadata = {
                'created_at': datetime.now().isoformat(),
                'django_version': getattr(settings, 'DJANGO_VERSION', 'unknown'),
                'total_objects': len(all_objects),
                'models': self._get_model_counts()
            }
            
            # Serialize data
            serialized_data = serializers.serialize('json', all_objects, indent=2)
            
            # Create backup structure
            backup_data = {
                'metadata': metadata,
                'data': json.loads(serialized_data)
            }
            
            # Write to file (compressed or uncompressed)
            if compress:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            size_mb = file_size / (1024 * 1024)
            
            self.stdout.write(f'✅ Backup created: {filename}')
            self.stdout.write(f'   Location: {filepath}')
            self.stdout.write(f'   Size: {size_mb:.2f} MB')
            self.stdout.write(f'   Objects: {len(all_objects)}')
            self.stdout.write(f'   Compressed: {"Yes" if compress else "No"}')
            
        except Exception as e:
            raise CommandError(f'Backup failed: {e}')
    
    def _restore_backup(self, backup_file, clear_first=False):
        """Restore data from backup file."""
        self.stdout.write(
            self.success_style(f'📥 Restoring from backup: {backup_file}')
        )
        
        # Find backup file
        if not os.path.isabs(backup_file):
            backup_file = os.path.join(self.backup_dir, backup_file)
        
        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file not found: {backup_file}')
        
        try:
            # Read backup file
            if backup_file.endswith('.gz'):
                with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            # Show backup info
            metadata = backup_data.get('metadata', {})
            self.stdout.write(f'📋 Backup Info:')
            self.stdout.write(f'   Created: {metadata.get("created_at", "Unknown")}')
            self.stdout.write(f'   Objects: {metadata.get("total_objects", "Unknown")}')
            
            # Clear existing data if requested
            if clear_first:
                self._clear_all_data()
            
            # Restore data
            with transaction.atomic():
                # Convert back to Django fixture format
                fixture_data = json.dumps(backup_data['data'])
                
                # Deserialize and save
                objects = serializers.deserialize('json', fixture_data)
                for obj in objects:
                    obj.save()
            
            self.stdout.write('✅ Data restored successfully')
            self._show_restored_counts()
            
        except Exception as e:
            raise CommandError(f'Restore failed: {e}')
    
    def _list_backups(self):
        """List available backup files."""
        self.stdout.write(
            self.success_style('📋 Available Backups:')
        )
        self.stdout.write('-' * 50)
        
        if not os.path.exists(self.backup_dir):
            self.stdout.write('No backup directory found.')
            return
        
        backup_files = [f for f in os.listdir(self.backup_dir) 
                       if f.startswith('backup_') and 
                       (f.endswith('.json') or f.endswith('.json.gz'))]
        
        if not backup_files:
            self.stdout.write('No backup files found.')
            return
        
        backup_files.sort(reverse=True)  # Most recent first
        
        for filename in backup_files:
            filepath = os.path.join(self.backup_dir, filename)
            file_size = os.path.getsize(filepath)
            size_mb = file_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            self.stdout.write(f'📁 {filename}')
            self.stdout.write(f'   Size: {size_mb:.2f} MB')
            self.stdout.write(f'   Modified: {modified_time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write('')
    
    def _get_all_objects(self):
        """Get all objects to backup in dependency order."""
        objects = []
        
        # Add objects in dependency order (parents before children)
        objects.extend(Brand.objects.all())
        objects.extend(Model.objects.all())
        objects.extend(Series.objects.all())
        objects.extend(Year.objects.all())
        objects.extend(BrandModelSeries.objects.all())
        objects.extend(Package.objects.all())
        objects.extend(BlurbGroup.objects.all())
        objects.extend(Blurb.objects.all())
        objects.extend(Match.objects.all())
        objects.extend(MatchItem.objects.all())
        
        return objects
    
    def _get_model_counts(self):
        """Get count of objects per model."""
        return {
            'Brand': Brand.objects.count(),
            'Model': Model.objects.count(),
            'Series': Series.objects.count(),
            'Package': Package.objects.count(),
            'Year': Year.objects.count(),
            'BlurbGroup': BlurbGroup.objects.count(),
            'Blurb': Blurb.objects.count(),
            'BrandModelSeries': BrandModelSeries.objects.count(),
            'Match': Match.objects.count(),
            'MatchItem': MatchItem.objects.count(),
        }
    
    def _clear_all_data(self):
        """Clear all maker app data."""
        self.stdout.write(f'{self.warning_style("⚠️  Clearing existing data...")}')
        
        with transaction.atomic():
            MatchItem.objects.all().delete()
            Match.objects.all().delete()
            BrandModelSeries.objects.all().delete()
            Blurb.objects.all().delete()
            BlurbGroup.objects.all().delete()
            Package.objects.all().delete()
            Year.objects.all().delete()
            Series.objects.all().delete()
            Model.objects.all().delete()
            Brand.objects.all().delete()
        
        self.stdout.write('✅ Existing data cleared')
    
    def _show_restored_counts(self):
        """Show counts of restored objects."""
        self.stdout.write('\n📊 Restored Data:')
        counts = self._get_model_counts()
        for model, count in counts.items():
            if count > 0:
                self.stdout.write(f'   {model}: {count}')
        
        self.stdout.write(f'\n💡 Use --list-backups to see all available backups')
        self.stdout.write(f'   Backup directory: {self.backup_dir}')