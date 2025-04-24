import streamlit as st
import tempfile
from outils_v1 import *
from constants import *
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client.http.models import Filter, FilterSelector

# Interface Streamlit
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

if not client.collection_exists(QDRANT_COLLECTION_v1):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_v1,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION_v1, embeddings=embedding_model)

# 🔥 Chargement du modèle Groq avec mise en cache
@st.cache_resource
def get_llm(llm_name):
    return ChatGroq(groq_api_key=GROQ_API_KEY, model_name=llm_name)

llm = get_llm(LLM_NAME_1)


st.title("📄 Lecteur de PDF avec PyMuPDF")

def clear_uploaded_files():
    """Réinitialisation des fichiers et de la session"""
    client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state.clear()
    st.session_state["file_uploader"] = None
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True) 

# Uploader dans la sidebar
uploaded_file = st.sidebar.file_uploader("📥 Charger un fichier PDF", type="pdf")

# Bouton pour réinitialiser toute la session et les documents indexés
if st.sidebar.button("🔄 Réinitialiser tout"):
    clear_uploaded_files()
    
# 🔄 Si un fichier est chargé, vider la collection Qdrant avant traitement
if uploaded_file is not None and st.session_state.get("last_uploaded_filename") != uploaded_file.name:
    client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state["last_uploaded_filename"] = uploaded_file.name

# Après extraction des articles depuis le PDF
if uploaded_file is not None:
    st.sidebar.success("✅ PDF chargé avec succès")

    # 🧼 Étape 1 : Extraire + nettoyer les articles
    articles_nettoyes = extraire_articles_pdf(uploaded_file)

    # 📑 Étape 2 : Séparer les articles avec un ID
    articles_decoupes = separer_articles(articles_nettoyes)

    # 🔎 Affichage simple
    for article in articles_decoupes:
        st.subheader(f"📰 Article {article['id']}")
        st.text(article['contenu'])

    # 📥 Indexation automatique dans Qdrant
    with st.spinner("🔄 Découpage en chunks et indexation..."):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        for article in articles_decoupes:
            chunks = text_splitter.split_text(article["contenu"])

            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "source_id": article["id"],
                        "chunk_id": i
                    }
                )
                for i, chunk in enumerate(chunks)
            ]

            vectorstore.add_documents(docs)

    st.success("✅ Tous les articles ont été indexés dans Qdrant automatiquement !")
