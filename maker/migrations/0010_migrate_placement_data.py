# Generated manually for MatchItem placement data migration

from django.db import migrations

def migrate_placement_data(apps, schema_editor):
    """
    Migrate existing MatchItem placement data to new format:
    - highlights -> exterior with is_highlight=True
    - options -> exterior with is_option=True
    - interior/exterior remain unchanged
    """
    MatchItem = apps.get_model('maker', 'MatchItem')
    
    # Update highlights items
    highlights_updated = MatchItem.objects.filter(placement='highlights').update(
        placement='exterior',
        is_highlight=True
    )
    
    # Update options items  
    options_updated = MatchItem.objects.filter(placement='options').update(
        placement='exterior',
        is_option=True
    )
    
    print(f"Migration completed:")
    print(f"  - {highlights_updated} highlights items -> exterior + is_highlight=True")
    print(f"  - {options_updated} options items -> exterior + is_option=True")

def reverse_placement_data(apps, schema_editor):
    """
    Reverse the migration by converting back to old placement format
    """
    MatchItem = apps.get_model('maker', 'MatchItem')
    
    # Reverse highlights
    highlights_reversed = MatchItem.objects.filter(
        placement='exterior', 
        is_highlight=True
    ).update(placement='highlights')
    
    # Reverse options  
    options_reversed = MatchItem.objects.filter(
        placement='exterior',
        is_option=True
    ).update(placement='options')
    
    # Reset boolean fields
    MatchItem.objects.all().update(is_highlight=False, is_option=False)
    
    print(f"Reverse migration completed:")
    print(f"  - {highlights_reversed} items -> highlights")
    print(f"  - {options_reversed} items -> options")

class Migration(migrations.Migration):

    dependencies = [
        ('maker', '0009_historicalmatchitem_is_highlight_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_placement_data, reverse_placement_data),
    ]