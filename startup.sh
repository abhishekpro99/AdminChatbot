#!/bin/bash

# Exit on error
set -e

# Collect static files (if needed)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations (safe to run each time)
echo "Applying database migrations..."
python manage.py migrate

# Pre-download Hugging Face models
echo "Preloading Hugging Face models..."

# Ensure cache directory is writable and exists in /tmp for Azure
export TRANSFORMERS_CACHE=/tmp/huggingface_cache
mkdir -p $TRANSFORMERS_CACHE

# Use inline Python to preload model into Azure's writable temp area
python <<EOF
from transformers import AutoModel, AutoTokenizer

model_name = "sentence-transformers/all-MiniLM-L6-v2"

print(f"Downloading model: {model_name}")
AutoTokenizer.from_pretrained(model_name, cache_dir="$TRANSFORMERS_CACHE")
AutoModel.from_pretrained(model_name, cache_dir="$TRANSFORMERS_CACHE")
EOF

# Start the Django app using gunicorn
echo "Starting Gunicorn server..."
exec gunicorn rag_project.wsgi:application \
  --bind=0.0.0.0:${PORT:-8000} \
  --workers=4 \
  --threads=4 \
  --timeout=120
