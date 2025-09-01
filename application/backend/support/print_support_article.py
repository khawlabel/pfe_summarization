from qdrant_client import QdrantClient
from constants import *

# Connexion à Qdrant
client = QdrantClient(QDRANT_URL, api_key=QDRANT_API)

# Nom de la collection
collection_name = QDRANT_COLLECTION_SUPPORT_4

# Nombre de points à afficher
nb_points = 10  # tu peux augmenter ce nombre

# Récupération des points
response = client.scroll(
    collection_name=collection_name,
    limit=nb_points,
    with_payload=True,
    with_vectors=False  # ou True si tu veux voir les vecteurs (souvent très longs)
)

# Affichage
print(f"--- Contenu de la collection '{collection_name}' ---\n")
for i, point in enumerate(response[0]):
    payload = point.payload
    print(f"🧠 Point {i+1}:")
    print(f"  📝 Résumé: {payload.get('resume')}")
    print(f"  📌 embedding_resume (taille): {len(payload.get('embedding_resume', []))}")
    print(f"  📌 embedding_source_like (taille): {len(payload.get('embedding_source_like', []))}")
    print("-" * 80)
