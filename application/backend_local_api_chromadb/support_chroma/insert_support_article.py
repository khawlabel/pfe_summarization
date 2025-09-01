import os
import json
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings

# === 1) Config ===
CHROMA_PATH = "./chroma_db"

MODEL_EMBEDDING2 = os.path.join(os.path.dirname(__file__), "../multilingual-e5-small")
JSON_FILE = os.path.join(os.path.dirname(__file__), "support_article_mediamarketing.json")

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING2)

embedding_model = get_embedding_model()

# === 2) Initialiser ChromaDB ===
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="collection_V0_support_mediamarketing")

# === 3) Charger les données ===
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

print("📂 JSON chargé :", JSON_FILE)
print("📊 Nombre d’articles :", len(data))

# === 4) Préparer les documents ===
ids = []
documents = []
metadatas = []
embeddings = []

for idx, item in enumerate(data):
    resume = item["resume"]
    texte = item["texte"]

    # Embedding du résumé (vecteur principal pour la recherche)
    emb_resume = embedding_model.embed_documents([resume])[0]

    ids.append(str(idx))
    documents.append(resume)  # on garde le résumé comme document principal
    metadatas.append({
        "resume": resume,
        "source": texte,
       })
    embeddings.append(emb_resume)  # vecteur indexé = celui du résumé

# === 5) Insertion ===
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings
)

print(f"✅ {len(ids)} documents insérés dans ChromaDB")

# === 6) Vérification immédiate ===
count = collection.count() if hasattr(collection, "count") else len(collection.get()["ids"])
print(f"📦 Nombre de documents dans la collection après insertion : {count}")
