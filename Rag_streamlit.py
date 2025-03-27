import streamlit as st
import tempfile
from constants import *
import os
from outils import extract_text
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from prompts import *

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

# 📂 Chargement des fichiers
st.sidebar.header("📂 Chargez vos fichiers :")
uploaded_files = st.sidebar.file_uploader(
    "Choisir des fichiers",
    type=["pdf", "mp3", "mp4"],
    accept_multiple_files=True
)

# ✅ Traitement et stockage des fichiers
def process_and_store_files(files):
    processed_files = []
    
    for file in files:
        suffix = os.path.splitext(file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        try:
            text = extract_text(temp_file_path)
            if text:
                metadata = {"file_name": file.name, "file_type": file.type}
                vectorstore.add_texts([text], metadatas=[metadata])
                processed_files.append(file.name)
        except ValueError as e:
            st.error(f"⚠️ Erreur lors de l'extraction du fichier {file.name} : {e}")
        finally:
            os.remove(temp_file_path)
    
    return processed_files

# 🔍 Récupération du contexte
def retrieve_context_with_metadata(query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(query)
    return "\n\n".join([f"📂 {doc.metadata.get('file_name', 'Inconnu')}\n{doc.page_content}" for doc in retrieved_docs])

# 📌 Chaînes de traitement
chain_chat = (
    {"context": itemgetter("context"), "question": itemgetter("question"), "language": itemgetter("language")}
    | prompt_chat | llm | StrOutputParser()
)

chain_resumer = (
    {"context": itemgetter("context"), "language": itemgetter("language")}
    | prompt_resumer | llm | StrOutputParser()
)

# 📩 Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📩 Affichage des messages précédents
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 🌟 Interface chat + résumé bien organisé
chat_container = st.container()

with chat_container:
    col1, col2 = st.columns([1, 3])  # Ajustement de la mise en page

    with col1:
        summarize_btn = st.button("📄 Résumer", use_container_width=True)

    with col2:
        user_input = st.chat_input("Pose ta question ici...")

# 💡 Gestion des actions après soumission
if summarize_btn:
    if not uploaded_files:
        st.warning("⚠️ Veuillez téléverser des fichiers avant de générer un résumé.")
    elif not lang:
        st.warning("⚠️ Veuillez sélectionner une langue pour le résumé.")
    else:
        processed_files = process_and_store_files(uploaded_files)
        if processed_files:
            query = "Fais un résumé clair et structuré des informations disponibles dans les sources."
            context = retrieve_context_with_metadata(query)
            summary = chain_resumer.invoke({"context": context, "language": lang})

            st.session_state.messages.append({"role": "assistant", "content": f"**Résumé du document :**\n\n{summary}"})

            with st.chat_message("assistant"):
                st.markdown(f"**Résumé du document :**\n\n{summary}")

if user_input:
    if not uploaded_files:
        st.warning("⚠️ Veuillez téléverser des fichiers avant de poser une question.")
    elif not lang:
        st.warning("⚠️ Veuillez sélectionner une langue pour poser votre question.")
    else:
        processed_files = process_and_store_files(uploaded_files)
        if processed_files:
            context = retrieve_context_with_metadata(user_input)
            response = chain_chat.invoke({"context": context, "question": user_input, "language": lang})

            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": response})

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                st.markdown(response)
