# Demo Data Setup Guide

The Pickles Maker application includes comprehensive demo data to help you explore its features. There are several methods to set up demo data, each suited for different use cases.

## 🚀 Quick Start (Recommended for New Users)

The easiest way to get started with demo data:

```bash
python manage.py setup_demo_data --clear --show-summary
```

This will:
- Clear any existing data
- Load comprehensive demo data
- Show a summary of what was loaded

## 📋 Available Methods

### 1. Custom Management Command (Recommended)

**Best for**: New users, development setup, testing

```bash
# Load demo data (preserves existing data)
python manage.py setup_demo_data

# Clear existing data and load fresh demo data
python manage.py setup_demo_data --clear

# Load and show detailed summary
python manage.py setup_demo_data --show-summary

# Use a specific fixture file
python manage.py setup_demo_data --fixture my_custom_data.json
```

**Features**:
- ✅ User-friendly progress messages
- ✅ Data validation and error handling
- ✅ Optional data clearing
- ✅ Detailed summaries
- ✅ Colorized output

### 2. Django Fixtures (Standard)

**Best for**: Version control, automated deployments, CI/CD

```bash
# Load demo data using Django's built-in command
python manage.py loaddata maker/fixtures/demo_data_clean.json

# Or load with history (larger file)
python manage.py loaddata maker/fixtures/demo_data.json
```

**Available Fixtures**:
- `demo_data_clean.json` - Core data without history (32KB, 244 records)
- `demo_data.json` - Complete data with history (138KB, includes audit trail)

### 3. Backup/Restore System (Advanced)

**Best for**: Production backups, migrating between environments

```bash
# Create a backup of current data
python manage.py backup_restore --backup

# List available backups
python manage.py backup_restore --list-backups

# Restore from backup
python manage.py backup_restore --restore backup_20250921_1557.json.gz

# Clear data before restoring
python manage.py backup_restore --restore backup_20250921_1557.json.gz --clear-before-restore
```

**Features**:
- ✅ Automatic compression
- ✅ Metadata tracking
- ✅ Database-agnostic
- ✅ Incremental backups
- ✅ File management

## 📊 What's Included in Demo Data

The demo data includes:

### Vehicle Data
- **5 Brands**: Tesla, BMW, Audi, Toyota, Volvo
- **13 Models**: Model 3, Model S, Model X, i4, XC90, A4, C-Class, etc.
- **13 Series**: Different generations and trims
- **33 Packages**: Various trim levels and option packages
- **5 Years**: 2020-2025

### Content System
- **2 BlurbGroups**: Parking Assistance, Charging Features
- **45 Blurbs**: Marketing content for different features
- **11 BrandModelSeries**: Vehicle configurations
- **16 Matches**: Content matching rules
- **74 MatchItems**: Specific content assignments

### Example Content Rules
- Tesla vehicles get electric-specific content
- Performance packages show sport features
- Parking assistance features use replacement logic
- Different content for interior, exterior, highlights, options

## 🔧 For Developers

### Creating New Fixtures

Export current data as fixtures:

```bash
# Clean export (recommended)
python manage.py dumpdata maker.Brand maker.Model maker.Series maker.Package maker.Year maker.BlurbGroup maker.Blurb maker.BrandModelSeries maker.Match maker.MatchItem --format=json --indent=2 > maker/fixtures/my_fixture.json

# Full export with history
python manage.py dumpdata maker --format=json --indent=2 > maker/fixtures/full_data.json
```

### File Locations

```
maker/
├── fixtures/
│   ├── demo_data_clean.json     # Main demo fixture
│   └── demo_data.json           # Full data with history
├── management/
│   └── commands/
│       ├── setup_demo_data.py   # User-friendly setup
│       └── backup_restore.py    # Backup system
└── models.py
```

### Backup Directory

Backups are stored in `./backups/` directory:

```
backups/
├── backup_20250921_1557.json.gz
├── backup_20250920_1042.json.gz
└── backup_20250919_1523.json.gz
```

## 🎯 Use Cases

### New Developer Setup
```bash
git clone <repo>
cd pickles
python manage.py migrate
python manage.py setup_demo_data --clear --show-summary
python manage.py runserver
```

### Production Backup
```bash
python manage.py backup_restore --backup
# Creates: backups/backup_YYYYMMDD_HHMMSS.json.gz
```

### Environment Migration
```bash
# On source environment
python manage.py backup_restore --backup

# On target environment  
python manage.py backup_restore --restore backup_20250921_1557.json.gz --clear-before-restore
```

### Testing Data Reset
```bash
python manage.py setup_demo_data --clear
# Resets to known good state
```

## 🛡️ Best Practices

### For Development
- Use `setup_demo_data --clear` for consistent test environment
- Keep fixtures in version control
- Use descriptive fixture names

### For Production
- Regular backups with `backup_restore --backup`
- Test restore procedures
- Keep multiple backup generations

### For Teams
- Share fixtures for consistent development data
- Document custom data requirements
- Use management commands for automation

## 🚨 Important Notes

### Data Dependencies
The demo data includes complex relationships:
- BrandModelSeries → Package many-to-many relationships
- Match → MatchItem with placement and priority
- Blurb → BlurbGroup with exclusion logic

### Loading Order
Django fixtures handle dependencies automatically, but when creating custom data:
1. Brands, Models, Series, Years first
2. BrandModelSeries second
3. Packages, BlurbGroups third
4. Blurbs fourth
5. Matches and MatchItems last

### Historical Data
- `demo_data.json` includes django-simple-history records
- `demo_data_clean.json` excludes history for smaller file size
- History is useful for audit trails but not needed for demo

## 🆘 Troubleshooting

### Command Not Found
```bash
# Make sure you're in the right directory
cd /path/to/pickles

# Make sure virtual environment is activated
source .venv/bin/activate  # or your venv path
```

### Permission Errors
```bash
# Create backups directory if needed
mkdir -p backups
chmod 755 backups
```

### Database Errors
```bash
# Run migrations first
python manage.py migrate

# Clear corrupted data
python manage.py setup_demo_data --clear
```

### Large File Issues
```bash
# Use clean fixture for smaller size
python manage.py setup_demo_data --fixture demo_data_clean.json

# Or use backup system with compression
python manage.py backup_restore --backup --compress
```

---

## 📞 Getting Help

If you encounter issues:
1. Check the command help: `python manage.py setup_demo_data --help`
2. Verify fixture files exist in `maker/fixtures/`
3. Ensure database migrations are up to date
4. Check Django admin at `/admin/` to verify data loaded correctly

The demo data provides a comprehensive foundation for exploring the Pickles Maker content generation system!