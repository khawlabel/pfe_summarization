import chromadb

# === Chemin absolu vers ta base Chroma ===
CHROMA_PATH = "./chroma_db"

# === Connexion ===
client = chromadb.PersistentClient(path=CHROMA_PATH)

print("📂 Dossier Chroma utilisé :", CHROMA_PATH)
print("📚 Collections disponibles :")

collections = client.list_collections()
if not collections:
    print("⚠️ Aucune collection trouvée dans ce dossier.")
else:
    for c in collections:
        try:
            coll = client.get_collection(c.name)
            total = coll.count()
        except Exception:
            total = "?"
        print(f"  - {c.name} (items: {total})")
