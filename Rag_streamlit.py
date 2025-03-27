import streamlit as st
import tempfile
import os
from outils import extract_text
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

st.sidebar.header("📂 Chargez vos fichiers : ")
uploaded_file = st.sidebar.file_uploader("Choisir un fichier", type=["pdf", "mp3", "mp4"])

st.sidebar.header("🌍 Selectionnez la langue de reponse :")
lang = st.sidebar.selectbox("Langue", ["", "Français", "Anglais", "Arabe"])  # Option vide par défaut

# 🌟 Boutons pour action
col1, col2 = st.columns(2)
with col1:
    summarize_btn = st.button("📝 Générer un Résumé")
with col2:
    ask_btn = st.button("💬 Poser une Question")



def process_and_store_file(file):
    """Extrait et stocke le texte du fichier dans Qdrant."""
    
    # Vérifie si le fichier est un objet BytesIO (cas de Streamlit)
    if hasattr(file, "read"):
        suffix = os.path.splitext(file.name)[1]  # Récupère l'extension du fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file.read())  # Sauvegarde temporairement le fichier
            temp_file_path = temp_file.name  # Récupère le chemin

    else:
        temp_file_path = file  # Si c'est déjà un chemin, on le garde tel quel
    try:
        text = extract_text(temp_file_path)
        if text:
            metadata = {"file_name": file.name, "file_type": file.type}
            vectorstore.add_texts([text], metadatas=[metadata])
            st.success(f"✅ Texte extrait et stocké depuis {file.name}")
    except ValueError as e:
        st.error(f"⚠️ Erreur lors de l'extraction : {e}")
    finally:
        os.remove(temp_file_path)  # Supprime le fichier temporaire après traitement

def retrieve_context_with_metadata(query):
    """Récupère les documents pertinents"""
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(query)
    return "\n\n".join([f"📂 {doc.metadata.get('file_name', 'Inconnu')}\n{doc.page_content}" for doc in retrieved_docs])

chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
chain_chat = ({"context": itemgetter("context"), "question": itemgetter("question"), "language": itemgetter("language")} | prompt_chat | llm | StrOutputParser())

# ⚠️ Condition pour exécuter les actions seulement si la langue est choisie et un bouton est cliqué
if lang and uploaded_file:
    if summarize_btn or ask_btn:
        process_and_store_file(uploaded_file)
        
        if summarize_btn:
            query = "Fais un résumé structuré des informations disponibles."
            context = retrieve_context_with_metadata(query)
            result = chain_resumer.invoke({"context": context, "language": lang})
            st.subheader("📝 Résumé généré")
            st.write(result)
        
        if ask_btn:
            query = st.text_input("❓ Pose ta question ici")
            if query:
                st.write("🔍 Question posée :", query)  # Debug

                context = retrieve_context_with_metadata(query)
                st.write("📂 Contexte récupéré :", context)  # Debug

                result = chain_chat.invoke({"context": context, "question": query, "language": lang})
                st.write("🤖 Réponse générée :", result)  # Debug

                st.subheader("🤖 Réponse du LLM")
                st.write(result)

else:
    st.warning("⚠️ Veuillez téléverser un fichier et choisir une langue avant de poursuivre.")
