import streamlit as st
from operator import itemgetter
from langchain.agents import initialize_agent, Tool, AgentType
from qdrant_client.models import VectorParams, Distance
from langchain.agents import AgentExecutor
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from constants import *
from outils import extract_text
from qdrant_client.http.models import Filter, FilterSelector
from prompts_v0_2 import *


# 🔗 Connexion à Qdrant avec mise en cache
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

client = get_qdrant_client()

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists(QDRANT_COLLECTION):
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embedding_model)

# 🔥 Chargement du modèle Groq avec mise en cache
@st.cache_resource
def get_llm(llm_name):
    return ChatGroq(groq_api_key=GROQ_API_KEY_3, model_name=llm_name)

llm = get_llm(LLM_NAME_4)

# Fonction pour récupérer le contexte pertinent
def retrieve_context_with_metadata(query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Récupère les 3 documents les plus pertinents
    retrieved_docs = retriever.invoke(query)
    return retrieved_docs
# 📌 Chaînes de traitement
chain_chat = ({"context": itemgetter("context"), "question": itemgetter("question")} | prompt_chat | llm | StrOutputParser())
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
# Outil de récupération de documents
def document_retrieval_tool(query):
    """Récupère les documents pertinents à partir de la base Qdrant et génère un résumé."""
    retrieved_docs = retrieve_context_with_metadata(query)
    context = " ".join([doc.page_content for doc in retrieved_docs])  # Combiner les textes des documents récupérés
    response = chain_chat.invoke({"context": context, "question": query})
    return response  # Retourner la sortie unique


# Définir les outils à utiliser par l'agent
tools = [
    Tool(
        name="Document Retrieval",
        func=document_retrieval_tool,
        description = "Récupère les informations pertinentes à partir des documents et répond aux questions des utilisateurs de manière claire, précise et structurée."

    )
]

# Initialiser l'agent avec des outils
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True  # Activer cette option
)

# Fonction pour générer un résumé via l'agent
def agent_chat(query, language="francais"):
    response = agent.run(query)  # Utiliser `invoke` pour un appel correct de l'agent
    return response


# Exemple d'utilisation de l'agent
query = "La couverture en fibre optique est-elle équilibrée entre toutes les wilayas d'Algérie ?"
language = "francais"

# Appeler l'agent pour générer un résumé
summary = agent_chat(query, language)

# Affichage du résumé généré
st.write("reponse : ", summary)
