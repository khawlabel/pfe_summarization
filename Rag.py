from outils import *
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from constants import *

# Connexion à Qdrant avec les variables chargées
client = QdrantClient(QDRANT_URL, api_key=QDRANT_API)

# Modèles Groq
llm1 = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_NAME_1)
llm2 = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_NAME_2)


# Charger le modèle d'embeddings
embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

# Récupérer la dimension du modèle
vector_size = embedding_model.client.get_sentence_embedding_dimension()


if not client.collection_exists(QDRANT_COLLECTION):
   client.create_collection(
      collection_name=QDRANT_COLLECTION,
      vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
   )

# Ajouter les documents à Qdrant
vectorstore = Qdrant(
    client=client,
    collection_name=QDRANT_COLLECTION,
    embeddings=embedding_model,
)

info = client.get_collection(QDRANT_COLLECTION)
print(f"📊 Nombre de vecteurs enregistrés : {info.points_count}")


def process_and_store_file(file_path,lang):
    """Extrait le texte d'un fichier et l'ajoute dans Qdrant."""
    extractedText = extract_text(file_path,lang)  # Ta fonction d'extraction
    print(extractedText)

    if extractedText:
        vectorstore.add_texts([extractedText])
        print(f"📥 Texte extrait et stocké depuis {file_path} ✅")
    else:
        print(f"⚠️ Aucun texte extrait depuis {file_path} ❌")


retriever = vectorstore.as_retriever()

qa_chain_1 = RetrievalQA.from_chain_type(llm=llm1, retriever=retriever, return_source_documents=True)
qa_chain_2 = RetrievalQA.from_chain_type(llm=llm2, retriever=retriever, return_source_documents=True)


# Exemple d'ajout de fichier
#files=["/content/ECHOUROUKELYAOUMI131020241a.pdf","/content/ELDJAZAIRELDJADIDA131020241a.pdf","/content/RadioOuargla141020241a.mp3","/content/Eliktisadia131020241a.mp4"]

files=["CHAINE1010920241a.mp3"]
langue="ar"
"""for file in files:
    process_and_store_file(file,langue)
    print("file proccessed")
"""
langues="francais" if langue=="fr" else "arabe"
query = f"Génère un résumé clair et concis en {langues}, en intégrant les informations clés de toutes les sources disponibles."

result = qa_chain_1.invoke(query)

print("📝 Réponse du LLM :")
print(result["result"])
print("\n📚 Documents utilisés :")
for doc in result["source_documents"]:
    print(doc.page_content)

"""#resume de mediamarketing

Le nombre de foyers connectés au réseau internet très haut débit en fibre optique jusqu'au domicile (FTTH) a dépassé le seuil de 1,5 million, a annoncé samedi 12 octobre 2024, le ministère de la Poste et des Télécommunications dans un communiqué. ""Cette évolution quantitative s'accompagne d'une amélioration qualitative de la vitesse de débit disponible pour les abonnés"", relève le communiqué, soulignant qu'Algérie Télécom a lancé des offres promotionnelles pour ceux souhaitant bénéficier de débits élevés allant jusqu'à 1 Gigabit/seconde sur demande"". Le nombre total de foyers connectés au réseau internet fixe, est passé de 3,5 millions au début de l'année 2020 à 5,8 millions en octobre 2024."
"""