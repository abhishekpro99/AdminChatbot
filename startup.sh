# Install dependencies
# echo "Installing Python dependencies..."
# pip install --upgrade pip
# pip install --prefer-binary -r requirements.txt

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations (optional, safe to run every time)
echo "Applying database migrations..."
python manage.py migrate


# Pre-download models
echo "Preloading Hugging Face models..."

# Use inline Python to preload models into cache
python <<EOF
from transformers import AutoModel, AutoTokenizer

# Replace with your actual model name(s)
model_name = "sentence-transformers/all-MiniLM-L6-v2"

print(f"Downloading model: {model_name}")
AutoTokenizer.from_pretrained(model_name, cache_dir="/home/site/wwwroot/.cache")
AutoModel.from_pretrained(model_name, cache_dir="/home/site/wwwroot/.cache")
EOF

# Set Hugging Face to use cached models
export TRANSFORMERS_CACHE=/home/site/wwwroot/.cache

# Run the Django app using gunicorn
echo "Starting Gunicorn server..."
gunicorn rag_project.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 4 --timeout 120
