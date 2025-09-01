import os
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from constants import *

MODEL_EMBEDDING2 = os.path.join(os.path.dirname(__file__), "../multilingual-e5-small")
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

client = get_qdrant_client()

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING2)

embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists(QDRANT_COLLECTION_SUPPORT_4):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_SUPPORT_4,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION_SUPPORT_4, embeddings=embedding_model)

import json

# Charger les résumés depuis le fichier JSON
file_path = os.path.join(os.path.dirname(__file__), "support_article_mediamarketing.json")
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Préparation des points à insérer dans Qdrant
points = []
for idx, item in enumerate(data):
    resume = item["resume"]
    texte = item["texte"]

    # Embedding du résumé
    emb_resume = embedding_model.embed_query(resume)

    # Embedding du texte source
    emb_source = embedding_model.embed_query(texte)

    points.append(
        PointStruct(
            id=idx,
            vector=emb_resume,  # vecteur principal
            payload={
                "resume": resume,
                "embedding_resume": emb_resume,
                "embedding_source_like": emb_source
            }
        )
    )

# Insertion des points dans Qdrant
client.upsert(collection_name=QDRANT_COLLECTION_SUPPORT_4, points=points)
print(f"{len(points)} points insérés dans la collection.")
