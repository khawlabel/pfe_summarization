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
from qdrant_client.http.models import Filter, FilterSelector
from prompts import *
import atexit

## App-V0-0 ##

# 📌 Interface Streamlit
st.set_page_config(page_title="🧠 AI Assistant", layout="wide")

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
def get_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name=LLM_NAME_1)

llm = get_llm()

# 🌍 Sélection de la langue
st.sidebar.header("🌍 Sélectionnez la langue de réponse :")
lang = st.sidebar.selectbox("Langue", ["", "Français", "Anglais", "Arabe"])

def clear_uploaded_files():
    client.delete(collection_name=QDRANT_COLLECTION, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state.clear()
    st.session_state["file_uploader"] = None  # Réinitialiser file_uploader
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)  # 🔥 Forcer un reload avec HTML


st.sidebar.header("📂 Chargez vos fichiers :")
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0

uploaded_files = st.sidebar.file_uploader(
    "Choisir des fichiers",
    type=["pdf", "mp3", "mp4"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state['file_uploader_key']}",
)
if st.sidebar.button("🗑️ Reinitisliser tout"):
    clear_uploaded_files()
    st.session_state["file_uploader_key"] += 1  # Changer la clé pour forcer la réinitialisation
    st.rerun()

st.session_state.setdefault("messages", [])
if "processed_files" not in st.session_state:
    st.session_state["processed_files"] = set()
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []
if "data_cleared" not in st.session_state:
    st.session_state["data_cleared"] = False  # Ajout d'un indicateur pour la suppression
st.session_state.setdefault("summarized_text", None)
st.session_state.setdefault("summary_generated", False)


def process_and_store_file(file):
    suffix = os.path.splitext(file.name)[1]  
    file_type = suffix.lstrip(".")  # Supprime le point pour obtenir 'pdf', 'mp4', etc.

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name
    
    try:
        text = extract_text(temp_file_path)
        if text:
            vectorstore.add_texts([text], metadatas=[{"file_name": file.name, "file_type": file_type}])
            st.session_state["processed_files"].add(file.name)
    except ValueError as e:
        st.error(f"⚠️ Erreur d'extraction : {e}")
    finally:
        os.remove(temp_file_path)


def retrieve_context_with_metadata(query):
    """Récupère les documents pertinents et intègre les métadonnées dans le contexte."""
    print("processed_files : ",len(st.session_state["processed_files"]))
    number_of_sources =  len(st.session_state["processed_files"])
    print("k :", number_of_sources)
    retriever = vectorstore.as_retriever(search_kwargs={"k": number_of_sources})
    retrieved_docs = retriever.invoke(query)

    formatted_context = "\n\n".join(
        [
            f"📂 Fichier: {doc.metadata.get('file_name', 'Inconnu')}\n"
            f"📄 Type: {doc.metadata.get('file_type', 'Inconnu')}\n"
            f"🔹 Contenu:\n{doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    return formatted_context
# 📌 Chaînes de traitement
chain_chat = ( {"context": itemgetter("context"), "question": itemgetter("question"), "language": itemgetter("language")} | prompt_chat | llm | StrOutputParser())
chain_resumer = ( {"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# 🛑 Suppression de la collection Qdrant UNE SEULE FOIS si c'est nécessaire
if uploaded_files and lang and not st.session_state["data_cleared"]:
    client.delete(collection_name=QDRANT_COLLECTION, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state["data_cleared"] = True  # ✅ On évite de supprimer encore

if uploaded_files and lang:
    for file in uploaded_files:
        if file.name not in st.session_state["processed_files"]:
            process_and_store_file(file)

prerequisites_missing = not lang or not uploaded_files
user_input = st.chat_input(
    "Pose ta question ici..." if not prerequisites_missing else "❌ Sélectionnez d'abord une langue et chargez au moins un fichier",
    disabled=prerequisites_missing
)

if user_input:
    context = retrieve_context_with_metadata(user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_stream = ""
        for chunk in chain_chat.stream({"context": context, "question": user_input, "language": lang}):
            if chunk:
                response_stream += chunk
                message_placeholder.markdown(response_stream)
        st.session_state["messages"].append({"role": "assistant", "content": response_stream})

if not prerequisites_missing and not st.session_state["summary_generated"]:  
    section_placeholder = st.empty()  # Permet de vider la section après le clic
    
    with section_placeholder.container():
        st.markdown("---")  # Ligne de séparation
        with st.chat_message("assistant"):
            st.markdown("💡 **Vous pouvez générer un résumé en cliquant sur le bouton ci-dessous.**")

        # ✅ Centrage du bouton "📖 Résumer"
        st.markdown(
            """
            <style>
            div.stButton > button {
                width: 250px;
                height: 50px;
                font-size: 18px;
                font-weight: bold;
                background-color: #4C585B;
                color: white;
                border-radius: 8px;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([2, 2, 2])
        with col2:
            bouton_resumer = st.button("📖 Résumer")

    if bouton_resumer:  # Dès que le bouton est cliqué
        section_placeholder.empty()  # Supprime le message et le bouton immédiatement

        # ✅ Afficher que l'utilisateur a demandé un résumé
        with st.chat_message("user"):
            st.markdown("📖 **Résumer**")

        # ✅ Ajouter la demande dans les messages
        st.session_state["messages"].append({"role": "user", "content": "📖 Résumer"})

        query = "Fais un résumé clair et structuré des informations disponibles."
        context = retrieve_context_with_metadata(query)

        # ✅ Génération du résumé en streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response_stream = ""

            for chunk in chain_resumer.stream({"context": context, "language": lang}):
                if chunk:
                    response_stream += chunk
                    message_placeholder.markdown(response_stream)

            st.session_state["summarized_text"] = response_stream  # Stocker le résumé complet

        # ✅ Ajouter le résumé dans les messages
        st.session_state["messages"].append({"role": "assistant", "content": st.session_state["summarized_text"]})

        # ✅ Mise à jour de l'état pour éviter de réafficher le bouton après refresh
        st.session_state["summary_generated"] = True
