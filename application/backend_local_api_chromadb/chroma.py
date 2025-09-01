import chromadb

# Créer un client local
client = chromadb.Client()

collection = client.create_collection(name="documents")
