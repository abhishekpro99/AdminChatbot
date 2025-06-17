#!/bin/bash

#!/bin/bash
set -e

echo "=== Starting Django App ==="
cd /home/site/wwwroot

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

echo "Applying database migrations..."
python manage.py migrate || echo "Migration failed, continuing..."

export TRANSFORMERS_CACHE=/tmp/huggingface_cache
mkdir -p "$TRANSFORMERS_CACHE"
MODEL_DIR="$TRANSFORMERS_CACHE/sentence-transformers__BAAI__bge-small-en-v1.5"

if [ ! -d "$MODEL_DIR" ]; then
  echo "Downloading model to $MODEL_DIR..."
  python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('BAAI/bge-small-en-v1.5', cache_folder='$TRANSFORMERS_CACHE')
" || echo "Warning: Model preloading failed."
else
  echo "Model already downloaded."
fi

echo "Starting Gunicorn server..."
exec gunicorn rag_project.wsgi:application \
  --bind=0.0.0.0:${PORT:-8000} \
  --workers=2 \
  --threads=2 \
  --timeout=240 \
  --log-level=info
