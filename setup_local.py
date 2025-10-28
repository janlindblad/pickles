#!/usr/bin/env python3
"""
Local development setup script for Pickles.
This script sets up the Django development environment without Docker.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment."""
    if not os.path.exists('.venv'):
        if not run_command("python3 -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = ".venv\\Scripts\\activate"
        pip_command = ".venv\\Scripts\\pip"
        python_command = ".venv\\Scripts\\python"
    else:
        activate_script = ".venv/bin/activate"
        pip_command = ".venv/bin/pip"
        python_command = ".venv/bin/python"
    
    print(f"💡 To activate the virtual environment, run:")
    print(f"   source {activate_script}")
    
    return pip_command, python_command

def install_dependencies(pip_command):
    """Install Python dependencies."""
    return run_command(f"{pip_command} install -r requirements.txt", "Installing dependencies")

def setup_database(python_command):
    """Run database migrations."""
    if not run_command(f"{python_command} manage.py migrate", "Running database migrations"):
        return False
    return True

def collect_static_files(python_command):
    """Collect static files for development."""
    return run_command(f"{python_command} manage.py collectstatic --noinput", "Collecting static files")

def create_superuser_if_needed(python_command):
    """Create superuser if environment variables are set."""
    superuser = os.getenv('SUPERUSER')
    superpass = os.getenv('SUPERPASS')
    
    if superuser and superpass:
        print(f"🔄 Creating superuser '{superuser}'...")
        script = f"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pickles.settings')
import django
django.setup()
from django.contrib.auth.models import User

username = '{superuser}'
password = '{superpass}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=f'{{username}}@example.com')
    print(f'Superuser "{{username}}" created successfully!')
else:
    print(f'Superuser "{{username}}" already exists')
"""
        
        # Write script to temporary file
        with open('temp_create_user.py', 'w') as f:
            f.write(script)
        
        success = run_command(f"{python_command} temp_create_user.py", "Creating superuser")
        
        # Clean up temp file
        if os.path.exists('temp_create_user.py'):
            os.remove('temp_create_user.py')
            
        return success
    else:
        print("💡 To create a superuser, set SUPERUSER and SUPERPASS environment variables")
        return True

def main():
    """Main setup function."""
    print("🥒 Pickles Local Development Setup")
    print("=" * 40)
    
    if not check_python_version():
        sys.exit(1)
    
    pip_command, python_command = setup_virtual_environment()
    
    if not install_dependencies(pip_command):
        sys.exit(1)
    
    if not setup_database(python_command):
        sys.exit(1)
    
    if not collect_static_files(python_command):
        sys.exit(1)
    
    create_superuser_if_needed(python_command)
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    print("2. Start the development server:")
    print("   python manage.py runserver")
    print("3. Open http://127.0.0.1:8000 in your browser")
    print("4. Access admin at http://127.0.0.1:8000/admin/")
    print("5. Create superuser at http://127.0.0.1:8000/setup/")

if __name__ == "__main__":
    main()