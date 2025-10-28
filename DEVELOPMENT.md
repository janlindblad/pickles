# Pickles Local Development Setup

This guide explains how to run Pickles locally without Docker for development purposes.

## Quick Start

### 1. Prerequisites
- Python 3.8+ installed on your system
- Git (to clone the repository)

### 2. Setup
```bash
# Clone the repository (if not already done)
git clone https://github.com/janlindblad/pickles.git
cd pickles

# Run the automated setup script
python3 setup_local.py
```

### 3. Run the Development Server
```bash
# Start the development server
./run_local.sh

# Or manually:
source .venv/bin/activate
python manage.py runserver
```

### 4. Access the Application
- **Main app**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/
- **Setup page**: http://127.0.0.1:8000/setup/

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 4. Create Superuser (Optional)
```bash
# Option 1: Using environment variables
export SUPERUSER=admin
export SUPERPASS=your_password
# Then visit http://127.0.0.1:8000/setup/

# Option 2: Using Django command
python manage.py createsuperuser
```

### 5. Start Development Server
```bash
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Copy the example file
cp .env.example .env
# Edit the .env file with your settings
```

Key variables:
- `DEBUG=True` - Enable debug mode for development
- `SUPERUSER=admin` - Username for superuser creation via /setup/
- `SUPERPASS=password` - Password for superuser creation via /setup/
- `SECRET_KEY=your-key` - Django secret key (generate a new one)

## Development vs Production

| Feature | Local Development | Docker (Production) |
|---------|------------------|-------------------|
| Server | Django dev server | Gunicorn WSGI |
| Port | 8000 (default) | 8080 |
| Debug | Enabled | Disabled |
| Static Files | Served by Django | Served by WhiteNoise |
| Logs | Console output | Container logs |
| Database | Local SQLite | Container SQLite |

## Advantages of Local Development

### ✅ **Benefits**
- **Direct log access** - See Django logs directly in your terminal
- **Faster development cycle** - No container rebuild needed
- **IDE integration** - Full debugging support in VS Code/PyCharm
- **File watching** - Auto-reload on code changes
- **Easy debugging** - Set breakpoints, inspect variables
- **Direct database access** - Query SQLite file directly

### 🔧 **Development Features**
- Auto-reload on file changes
- Detailed error pages with stack traces
- Django debug toolbar (if installed)
- Direct access to `manage.py` commands
- Easy database inspection and migration testing

## Switching Between Local and Docker

### To Local Development:
```bash
# Setup local environment
python3 setup_local.py

# Start local server
./run_local.sh
```

### To Docker:
```bash
# Build and run container
docker build -t pickles-app .
docker run -p 8080:8080 -e SUPERUSER=admin -e SUPERPASS=password pickles-app
```

## Common Development Tasks

### Run Tests
```bash
source .venv/bin/activate
python manage.py test
```

### Create Migrations
```bash
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

### Access Django Shell
```bash
source .venv/bin/activate
python manage.py shell
```

### Collect Static Files
```bash
source .venv/bin/activate
python manage.py collectstatic
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Permission Errors
```bash
# Make scripts executable
chmod +x setup_local.py
chmod +x run_local.sh
```