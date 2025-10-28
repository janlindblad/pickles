#!/bin/bash
# Local development server runner for Pickles

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run './setup_local.py' first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Django not found. Run './setup_local.py' first."
    exit 1
fi

echo "🥒 Starting Pickles development server..."
echo "📍 Local URLs:"
echo "   Main app: http://127.0.0.1:8000/"
echo "   Admin: http://127.0.0.1:8000/admin/"
echo "   Setup: http://127.0.0.1:8000/setup/"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Start Django development server
python manage.py runserver