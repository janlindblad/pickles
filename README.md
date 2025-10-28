# Pickles Maker

**Intelligent Vehicle Content Generation System**

Pickles Maker is a Django-based application that generates dynamic marketing content for electric and hybrid vehicles. It uses a sophisticated matching system to deliver contextually appropriate content based on vehicle specifications, packages, and features.

## 🚀 Quick Start Options

**Choose your preferred development approach:**

### 🖥️ Local Development (Recommended for Development)
- ✅ **Direct log access** in your terminal
- ✅ **Faster development cycle** (no container rebuilds)
- ✅ **Full IDE integration** and debugging support
- ✅ **Auto-reload** on code changes

```bash
# One-command setup
python3 setup_local.py

# Start development server
./run_local.sh
# or: source .venv/bin/activate && python manage.py runserver
```

📖 **[See detailed local development guide →](DEVELOPMENT.md)**

### 🐳 Docker Deployment (Recommended for Production)
- ✅ **Production-ready** with Gunicorn + WhiteNoise
- ✅ **Consistent environment** across all systems
- ✅ **Easy deployment** to cloud platforms

```bash
# Build and run
docker build -t pickles-app .
docker run -p 8080:8080 -e SUPERUSER=admin -e SUPERPASS=password pickles-app
```

**Cloud deployment:** `ghcr.io/janlindblad/pickles:latest`

## ✨ Features

- **Dynamic Content Generation**: Automatically generates marketing content based on vehicle selection
- **BlurbGroup System**: Intelligent content exclusion and replacement logic (e.g., "Automatic parking" replaces "Parking assist")
- **Package-Specific Content**: Different content for different trim levels and option packages
- **Responsive Design**: Works seamlessly across desktop, tablet, and mobile devices
- **Admin Interface**: Comprehensive Django admin for content management
- **Content Categories**: Organized into Interior, Exterior, Highlights, and Options
- **Priority System**: Smart content selection based on importance and relevance

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/janlindblad/pickles.git
   cd pickles
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings (database, secret key, etc.)
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load demo data** (Recommended for first-time users)
   ```bash
   python manage.py setup_demo_data --clear --show-summary
   ```

7. **Create admin user**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main application: http://localhost:8000/
   - Admin interface: http://localhost:8000/admin/

## 🗄️ Demo Data Setup

Pickles Maker includes comprehensive demo data to help you explore its features. Choose the method that best fits your needs:

### Option 1: Custom Management Command (Recommended)

**Best for**: New users, development setup, testing

```bash
# Quick setup with summary (recommended for first-time users)
python manage.py setup_demo_data --clear --show-summary

# Load without clearing existing data
python manage.py setup_demo_data

# Use specific fixture
python manage.py setup_demo_data --fixture demo_data_clean.json
```

**Features:**
- ✅ User-friendly colored output
- ✅ Progress messages and validation
- ✅ Optional data clearing
- ✅ Detailed summaries with tips
- ✅ Error handling and recovery

### Option 2: Django Fixtures (Standard)

**Best for**: Version control, CI/CD, automated deployments

```bash
# Load clean demo data (recommended)
python manage.py loaddata maker/fixtures/demo_data_clean.json

# Load complete data with history
python manage.py loaddata maker/fixtures/demo_data.json
```

**Available Files:**
- `demo_data_clean.json` - 32KB, 244 records (no history)
- `demo_data.json` - 138KB, full data with audit trail

### Option 3: Backup/Restore System (Advanced)

**Best for**: Production backups, environment migration

```bash
# Create compressed backup
python manage.py backup_restore --backup

# List all backups
python manage.py backup_restore --list-backups

# Restore from backup
python manage.py backup_restore --restore backup_20250921_1557.json.gz

# Clear and restore
python manage.py backup_restore --restore backup.json.gz --clear-before-restore
```

### What's Included in Demo Data

- **5 Brands**: Tesla, BMW, Audi, Toyota, Volvo
- **13 Models**: Model 3, Model S, i4, XC90, etc.
- **45 Blurbs**: Marketing content for different features
- **2 BlurbGroups**: Parking Assistance, Charging Features
- **74 MatchItems**: Content rules and assignments

For detailed setup instructions, see [DEMO_DATA_SETUP.md](DEMO_DATA_SETUP.md).

## ⚙️ Configuration

### Application Settings

The main application behavior can be configured in `maker/constants.py`:

```python
# Content generation character limits per category
CONTENT_LIMITS = {
    'interior': 500,
    'exterior': 500, 
    'highlights': 600,  # Highlights get more space
    'options': 400,     # Options get less space
}

# Content generation settings
CONTENT_SEPARATOR = ' '   # How to join multiple blurbs
CONTENT_ENDING = ''       # Content ending (empty since blurbs end with dots)

# UI messaging
MESSAGES = {
    'no_matches_found': 'No content rules found for this selection...',
    'content_generated': 'Content generated successfully.',
    'content_truncated': 'Content was truncated to fit character limits.',
}

# Default fallback content when no matches are found
FALLBACK_CONTENT = {
    'interior': '',
    'exterior': '',
    'highlights': '',
    'options': '',
}
```

### Environment Variables

Configure your installation by copying `.env.example` to `.env` and updating:

```bash
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite default, PostgreSQL recommended for production)
DATABASE_URL=sqlite:///db.sqlite3

# Optional: Additional settings
TIME_ZONE=UTC
LANGUAGE_CODE=en-us
```

## 🏗️ Application Architecture

### Dependency Tree
```
pickles (project settings)
└── maker (core models/UI)
    └── groker (datasheet parsing) [future]
```

### Key Models

- **Brand, Model, Series**: Vehicle hierarchy
- **Package**: Trim levels and option packages
- **Year**: Model years
- **BrandModelSeries**: Links brands/models/series with year ranges
- **BlurbGroup**: Content exclusion groups
- **Blurb**: Marketing content snippets
- **Match**: Content matching rules
- **MatchItem**: Specific content assignments

### Content Generation Flow

1. User selects Brand, Model, Year, Package
2. System finds matching BrandModelSeries
3. Matches are evaluated against selection criteria
4. MatchItems are collected and filtered through BlurbGroups
5. Content is generated with character limits and priorities
6. Results are returned as JSON for dynamic display

## 🎯 Usage Examples

### Basic Content Generation

1. **Visit the main application** at http://localhost:8000/
2. **Select vehicle criteria**: Brand, Model, Year, Package
3. **View generated content** in four categories:
   - **Interior**: Seating, technology, comfort features
   - **Exterior**: Design, lighting, aerodynamics
   - **Highlights**: Key selling points and premium features
   - **Options**: Additional packages and accessories

### Admin Interface

1. **Access admin** at http://localhost:8000/admin/
2. **Manage content**:
   - Create and edit Blurbs
   - Set up BlurbGroups for content exclusion
   - Configure Matches and MatchItems
   - Manage vehicle data (Brands, Models, etc.)

### BlurbGroup Examples

**Parking Assistance Group** (max_items=1):
- "Automatic parking" (priority: 10) ← **Selected**
- "Advanced parking sensors" (priority: 7)
- "Basic parking assist" (priority: 5)

*Result*: Only "Automatic parking" appears, replacing lower-priority alternatives.

## 🔧 Development

### Project Structure

```
pickles/
├── maker/                    # Core application
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints and views
│   ├── admin.py             # Django admin configuration
│   ├── constants.py         # Configuration settings
│   ├── fixtures/            # Demo data fixtures
│   └── management/          # Custom management commands
├── templates/               # HTML templates
├── static/                  # CSS, JavaScript, images
├── pickles/                 # Django project settings
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

### Development Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**
   ```bash
   python manage.py test
   python manage.py check
   ```

3. **Run with demo data**
   ```bash
   python manage.py setup_demo_data --clear
   python manage.py runserver
   ```

4. **Create pull request** against main branch

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test maker

# Run with coverage (if installed)
coverage run manage.py test
coverage report
```

## 🛠️ Advanced Features

### Content Exclusion System

The BlurbGroup system prevents duplicate or conflicting content:

- **Replacement Logic**: Higher priority items replace lower priority ones
- **Max Items Control**: Configure how many items per group
- **Automatic Deduplication**: Same blurb never appears twice
- **Cross-Category Support**: Groups work across Interior, Exterior, etc.

### Package-Specific Content

Different packages show appropriate content:

- **Base Package**: Standard features, value positioning
- **Premium Package**: Luxury features, advanced technology
- **Performance Package**: Sport styling, performance features
- **Universal Content**: Safety, core features (all packages)

### API Endpoints

- `GET /maker/packages/` - Get packages for brand/model/year
- `GET /maker/content/` - Generate content for selection
- Both endpoints return JSON for dynamic frontend updates

## 📖 Documentation

- **[Demo Data Setup Guide](DEMO_DATA_SETUP.md)** - Comprehensive setup instructions
- **[Code Contribution Guidelines](contribution_guidelines.txt)** - Development standards
- **Django Admin** - Built-in documentation at /admin/doc/ (if enabled)

## 🤝 Contributing

We welcome contributions! Please see our [contribution guidelines](contribution_guidelines.txt) for:

- Code standards and style
- Database and model guidelines  
- Testing requirements
- Security considerations
- Pull request process

### Quick Contributing Guide

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code standards** in contribution_guidelines.txt
4. **Add tests** for new functionality
5. **Ensure all tests pass**: `python manage.py test`
6. **Submit pull request** with description of changes

## 📊 Production Deployment

### Database

While SQLite works for development, use PostgreSQL for production:

```bash
pip install psycopg2-binary
# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/pickles_db
```

### Static Files

```bash
python manage.py collectstatic
```

### Security Settings

Update `.env` for production:

```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Backup Strategy

```bash
# Regular automated backups
python manage.py backup_restore --backup

# Schedule with cron
0 2 * * * cd /path/to/pickles && python manage.py backup_restore --backup
```

## 🔍 Troubleshooting

### Common Issues

**Demo data not loading:**
```bash
# Ensure you're in the right directory and venv is activated
python manage.py setup_demo_data --clear --show-summary
```

**Admin interface not accessible:**
```bash
# Create superuser account
python manage.py createsuperuser
```

**Static files not loading:**
```bash
# Collect static files
python manage.py collectstatic
```

**Database errors:**
```bash
# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py setup_demo_data --clear
```

### Getting Help

1. Check the [Demo Data Setup Guide](DEMO_DATA_SETUP.md)
2. Review [contribution guidelines](contribution_guidelines.txt)
3. Verify all dependencies: `pip install -r requirements.txt`
4. Ensure migrations are current: `python manage.py migrate`
5. Test with fresh demo data: `python manage.py setup_demo_data --clear`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Django and Python
- Uses django-simple-history for audit trails
- Responsive design with modern CSS
- Icons from Unicode symbols (no external dependencies)

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check existing documentation
- Review the admin interface for data validation
- Test with the included demo data

---

**Ready to explore vehicle content generation?**

```bash
python manage.py setup_demo_data --clear --show-summary
python manage.py runserver
```

Visit http://localhost:8000/ and start generating content! 🚀