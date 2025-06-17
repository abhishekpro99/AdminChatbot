#!/bin/bash

#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

echo "=== Starting Django App ==="

# 1. Static files (only needed if using Django's static handling)
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

# 2. Run database migrations
echo "Applying database migrations..."
python manage.py migrate || echo "Migration failed, continuing..."

# 3. Preload Hugging Face model ONLY IF not cached
echo "Preloading Hugging Face model into Azure temp dir..."
export TRANSFORMERS_CACHE=/tmp/huggingface_cache
mkdir -p "$TRANSFORMERS_CACHE"

MODEL_DIR="$TRANSFORMERS_CACHE/sentence-transformers__all-MiniLM-L6-v2"
if [ ! -d "$MODEL_DIR" ]; then
  echo "Downloading model to $MODEL_DIR..."
  python -c "
from transformers import AutoTokenizer, AutoModel
model = 'sentence-transformers/all-MiniLM-L6-v2'
AutoTokenizer.from_pretrained(model, cache_dir='$TRANSFORMERS_CACHE')
AutoModel.from_pretrained(model, cache_dir='$TRANSFORMERS_CACHE')
" || echo "Warning: Model preloading failed."
else
  echo "Model already downloaded."
fi

# 4. Start Gunicorn server
echo "Starting Gunicorn server..."
exec gunicorn rag_project.wsgi:application \
  --bind=0.0.0.0:${PORT:-8000} \
  --workers=2 \
  --threads=2 \
  --timeout=180 \
  --log-level=info
