#!/bin/bash

# Django LMS Deployment Script
# For PythonAnywhere or similar hosting

echo "=========================================="
echo "Django LMS Deployment Script"
echo "=========================================="

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "1. Creating virtual environment..."
python -m venv venv

echo ""
echo "2. Activating virtual environment..."
source venv/bin/activate

echo ""
echo "3. Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "4. Creating .env file if not exists..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
SECRET_KEY=change-this-to-a-secure-random-key
DEBUG=False
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_STORE_PASSWORD=your_password
SSLCOMMERZ_SANDBOX=True
BASE_URL=https://yourusername.pythonanywhere.com
EOF
    echo ".env file created! Please update it with your settings."
fi

echo ""
echo "5. Running migrations..."
python manage.py migrate

echo ""
echo "6. Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "7. Creating superuser (optional)..."
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your settings"
echo "2. Configure WSGI file in PythonAnywhere web tab"
echo "3. Set up static files in PythonAnywhere:"
echo "   - URL: /static/ -> /home/username/lms_ai/staticfiles"
echo "   - URL: /media/ -> /home/username/lms_ai/media"
echo "4. Reload web app"
