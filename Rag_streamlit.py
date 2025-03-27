import streamlit as st 
import tempfile
import os
from operator import itemgetter
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from constants import *
from outils_khawla import extract_text
from qdrant_client.http.models import Filter
from prompts import *

# 🔑 Clés API & Configuration
QDRANT_API="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.Fau1FEDosaMc3jteRJi2TtaGgq33VxjbFcY6_p3p8w0"
QDRANT_URL="https://08d055a0-1eb2-45c5-9e9a-64e741bba5ec.europe-west3-0.gcp.cloud.qdrant.io"
LLM_NAME_1="llama3-8b-8192"
GROQ_API_KEY="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"
QDRANT_COLLECTION="my_collection"

# 🎯 Initialisation Qdrant
client = QdrantClient(QDRANT_URL, api_key=QDRANT_API)
embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists(QDRANT_COLLECTION):
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embedding_model)

# 🔥 Chargement du modèle Groq
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_NAME_1)

# 📌 Interface Streamlit
st.set_page_config(page_title="🧠 AI Assistant", layout="wide")

# 🌍 Sélection de la langue
st.sidebar.header("🌍 Sélectionnez la langue de réponse :")
lang = st.sidebar.selectbox("Langue", ["", "Français", "Anglais", "Arabe"])

def clear_uploaded_files():
    """ Supprime uniquement les vecteurs et réinitialise les fichiers uploadés. """
    # Create a filter to match all points
    filter_all = Filter(
        must=[]  # Empty filter matches all points
    )
    client.delete(QDRANT_COLLECTION, filter=filter_all)
    st.session_state.pop("file_uploader", None)  # Réinitialise le file_uploader
    st.session_state["processed_files"] = set()  # Réinitialise la liste des fichiers traités
    st.session_state["uploaded_files"] = []  # Réinitialise la liste des fichiers uploadés
    st.rerun()

# 📂 Chargement des fichiers
st.sidebar.header("📂 Chargez vos fichiers :")
uploaded_files = st.sidebar.file_uploader("Choisir des fichiers", type=["pdf", "mp3", "mp4"], accept_multiple_files=True, key="file_uploader")

# Bouton pour supprimer les fichiers et vider la base de données
if st.sidebar.button("🗑️ Supprimer les fichiers et vider la base"):
    clear_uploaded_files()


# 📩 Initialisation de l'historique et des fichiers traités
st.session_state.setdefault("messages", [])
st.session_state.setdefault("processed_files", set())
st.session_state.setdefault("summarized_text", None)

# ✅ Traitement et stockage du fichier
def process_and_store_file(file):
    """ Enregistre temporairement un fichier, extrait son texte et l'ajoute à Qdrant. """
    suffix = os.path.splitext(file.name)[1]  
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name
    
    try:
        text = extract_text(temp_file_path)
        if text:
            vectorstore.add_texts([text], metadatas=[{"file_name": file.name, "file_type": file.type}])
            st.session_state["processed_files"].add(file.name)
    except ValueError as e:
        st.error(f"⚠️ Erreur d'extraction : {e}")
    finally:
        os.remove(temp_file_path)  # Supprime le fichier temporaire

# 🔍 Récupération du contexte
def retrieve_context(query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return "\n\n".join([doc.page_content for doc in retriever.invoke(query)])

# 📌 Chaînes de traitement
chain_chat = ( {"context": itemgetter("context"), "question": itemgetter("question"), "language": itemgetter("language")} | prompt_chat | llm | StrOutputParser())
chain_resumer = ( {"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())

# 📩 Affichage des messages précédents
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 📂 Traitement des nouveaux fichiers
if uploaded_files and lang:
    for file in uploaded_files:
        if file.name not in st.session_state["processed_files"]:
            process_and_store_file(file)

# 📖 Bouton de résumé
if lang and uploaded_files and st.session_state["summarized_text"] is None:
    if st.button("📖 Résumer"):
        query = "Fais un résumé clair et structuré des informations disponibles."
        context = retrieve_context(query)
        st.session_state["summarized_text"] = chain_resumer.invoke({"context": context, "language": lang})
        st.session_state["messages"].append({"role": "assistant", "content": st.session_state["summarized_text"]})
        st.rerun()

# 🌟 Interface chat
prerequisites_missing = not lang or not uploaded_files
user_input = st.chat_input(
    "Pose ta question ici..." if not prerequisites_missing else "❌ Sélectionnez d'abord une langue et chargez au moins un fichier",
    disabled=prerequisites_missing
)

if user_input:
    context = retrieve_context(user_input)
    response = chain_chat.invoke({"context": context, "question": user_input, "language": lang})
    
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": response})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown(response)
