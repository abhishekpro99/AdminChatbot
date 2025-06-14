# Install dependencies
echo "Installing Python dependencies..."
# pip install --upgrade pip
# pip install --prefer-binary -r requirements.txt

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations (optional, safe to run every time)
echo "Applying database migrations..."
python manage.py migrate

# Run the Django app using gunicorn
echo "Starting Gunicorn server..."
gunicorn rag_project.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 4 --timeout 120
