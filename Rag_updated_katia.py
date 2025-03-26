from outils import *
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from constants import *
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from prompts import *
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

number_of_sources=4
retriever = vectorstore.as_retriever(search_kwargs={"k": number_of_sources})

#qa_chain_1 = RetrievalQA.from_chain_type(llm=llm1, retriever=retriever, return_source_documents=True)
qa_chain_2 = RetrievalQA.from_chain_type(llm=llm2, retriever=retriever, return_source_documents=True)


# Exemple d'ajout de fichier
#files=["pfe_summarization/data/ECHOUROUKELYAOUMI131020241a.pdf","pfe_summarization/data/ELDJAZAIRELDJADIDA131020241a.pdf","pfe_summarization/data/RadioOuargla141020241a.mp3","pfe_summarization/data/Eliktisadia131020241a.mp4"]

files=["pfe_summarization/data/ECHOUROUKELYAOUMI131020241a.pdf"]
langue="ar"

"""for file in files:
    process_and_store_file(file,langue)
    print("file proccessed")
"""


chain_resumer = (
    {
        "context": itemgetter("context"),
        "language": itemgetter("language"),
    }
    | prompt_resumer
    | llm1
    | StrOutputParser()
)
chain_chat = (
    {
        "context": itemgetter("context"),
        "question": itemgetter("question"),
        "language": itemgetter("language"),
    }
    | prompt_chat
    | llm1
    | StrOutputParser()
)
# Demander le mode à l'utilisateur
mode = input("Voulez-vous un résumé (1) ou poser une question (2) ? ").strip()
if mode == "1":
    query = "Fais un résumé clair et structuré des informations disponibles dans les sources."

    retrieved_docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    result = chain_resumer.invoke({"context": context, "language":"francais"})

    print("\n📝 Résumé généré :")
    print(result)
elif mode == "2":
    query = "Ces sources parle de quoi ?"
    
    retrieved_docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    result = chain_chat.invoke({"context": context,"question": query, "language": "arabe"})

    print("\n🤖 Réponse du LLM :")
    print(result)


"""
print("\n📚 Documents utilisés :")
for doc in retrieved_docs:
    print(doc.page_content)
"""
"""
#titre :
Plus de 1,5 million de foyers connectés au FTTH en Algérie.

# resume de mediamarketing :

Le nombre de foyers connectés au réseau internet très haut débit en fibre optique jusqu'au domicile
 (FTTH) a dépassé le seuil de 1,5 million, a annoncé samedi 12 octobre 2024, le ministère de
   la Poste et des Télécommunications dans un communiqué. ""Cette évolution quantitative
     s'accompagne d'une amélioration qualitative de la vitesse de débit disponible pour les 
     abonnés"", relève le communiqué, soulignant qu'Algérie Télécom a lancé des offres 
     promotionnelles pour ceux souhaitant bénéficier de débits élevés allant jusqu'à 1 
     Gigabit/seconde sur demande"". Le nombre total de foyers connectés au réseau internet fixe, 
     est passé de 3,5 millions au début de l'année 2020 à 5,8 millions en octobre 2024."
"""

"""Plus de 1,5 million de foyers algériens sont maintenant connectés en fibre optique, 
selon une déclaration de la ministre des Télécommunications. De plus, le nombre de foyers connectés à l'internet
 fixe a atteint 5,8 millions. Cette croissance est due à l'accent mis sur la numérisation et les directives du
   président de la République. Les utilisateurs bénéficient ainsi de vitesses de téléchargement élevées et
     d'accès à l'internet fixe."""