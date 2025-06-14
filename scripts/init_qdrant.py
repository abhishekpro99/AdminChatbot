# scripts/init_qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

qdrant = QdrantClient("http://localhost:6333")

collection_name = "documents"

if not qdrant.collection_exists(collection_name):
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
