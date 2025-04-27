import streamlit as st
from outils_v1 import *
from constants import *
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import Filter, FilterSelector
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Qdrant
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from prompts_v1_khawla import *
from operator import itemgetter
from prompts_v0_2 import *
# Interface Streamlit
st.set_page_config(page_title="🧠 AI Assistant PDF", layout="wide")

# Initialisation du cache
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING_v1)

@st.cache_resource
def get_llm(llm_name):
    return ChatGroq(groq_api_key=GROQ_API_KEY_2, model_name=llm_name)

@st.cache_resource
def get_reranker_model(model_name):
    return HuggingFaceCrossEncoder(model_name=model_name)

# Clients et modèles
client = get_qdrant_client()
embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

# Création collection si besoin
if not client.collection_exists(QDRANT_COLLECTION_v1):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_v1,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION_v1, embeddings=embedding_model)
llm = get_llm(LLM_NAME_4)
reranker_model = get_reranker_model("BAAI/bge-reranker-v2-m3")
llm2=get_llm(LLM_NAME_4)

# 🔁 Réinitialisation
def clear_uploaded_files():
    client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state.clear()
    st.session_state["file_uploader"] = None
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)

st.sidebar.title("🗂️ Chargement PDF")
uploaded_file = st.sidebar.file_uploader("📥 Charger un PDF", type="pdf")
if st.sidebar.button("🔄 Réinitialiser"):
    clear_uploaded_files()

# Mémoire temporaire des articles originaux (non chunkés)
if "articles_originaux" not in st.session_state:
    st.session_state["articles_originaux"] = {}

# Traitement du PDF
if uploaded_file is not None:
    if st.session_state.get("last_uploaded_filename") != uploaded_file.name:
        client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))
        st.session_state["last_uploaded_filename"] = uploaded_file.name

        st.sidebar.success("✅ PDF chargé")

        # Extraire et découper
        articles_nettoyes = extraire_articles_pdf(uploaded_file)
        articles_decoupes = separer_articles(articles_nettoyes)

        st.session_state["articles_originaux"] = {a["id"]: a["contenu"] for a in articles_decoupes}
        st.sidebar.info(f"🧾 Articles détectés : {len(articles_decoupes)}")

        # Découpage en chunks + indexation
        with st.spinner("🔄 Indexation des articles..."):
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            seen_chunks = set()
            all_chunks = []

            for article in articles_decoupes:
                if "contenu" not in article or not article["contenu"]:
                    continue

                chunks = splitter.split_text(article["contenu"])
                docs = []
                for i, chunk in enumerate(chunks):
                    clean_chunk = chunk.strip()
                    if clean_chunk not in seen_chunks:
                        seen_chunks.add(clean_chunk)
                        docs.append(Document(
                            page_content=clean_chunk,
                            metadata={"source_id": article["id"], "chunk_id": i}
                        ))

                if docs:
                    vectorstore.add_documents(docs)

        st.success("✅ Indexation terminée !")

    else:
        st.sidebar.info("📄 PDF déjà chargé et indexé.")

chain_client = ({"context": itemgetter("context"), "user_query": itemgetter("user_query")} | prompt_client | llm | StrOutputParser())
chain_titre = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre | llm | StrOutputParser())
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
chain_resumer_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer_general | llm | StrOutputParser())
chain_titre_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre_general | llm | StrOutputParser())

# Recherche par requête
st.title("🔎 Recherche intelligente dans le PDF")
query = st.text_input("💬 Posez votre question :")

if query:
    st.info("📡 Recherche...")

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 50})
    compressor = CrossEncoderReranker(model=reranker_model, top_n=10)
    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

    matching_chunks = compression_retriever.invoke(query)

    if matching_chunks:
        st.success(f"✅ {len(matching_chunks)} chunks pertinents")
        
        # 🔁 Récupérer les source_id uniques
        ids_utilises = {chunk.metadata.get("source_id") for chunk in matching_chunks}

        st.info(f"📰 Articles correspondants : {len(ids_utilises)}")

        # 📝 Stocker tous les titres et tous les résumés
        tous_les_titres = []
        tous_les_resumes = []

        # 🔹 Boucler sur chaque article séparément
        for source_id in ids_utilises:
            article_complet = st.session_state["articles_originaux"].get(source_id, "")
            if not article_complet:
                continue

            st.subheader(f"=== Article {source_id} ===")
            
            # 📤 Générer le titre pour cet article
            titre = ""
            for chunk in chain_titre.stream({"context": article_complet, "language": "francais"}):
                if chunk:
                    titre += chunk

            # 📤 Générer le résumé normal pour cet article
            resume = ""
            for chunk in chain_resumer.stream({"context": article_complet, "language": "francais"}):
                if chunk:
                    resume += chunk


            st.markdown(
                f"""<div style="text-align: justify;">
                        <strong>Titre</strong> : {titre}<br><br>
                        <strong>Résumé normal</strong> : {resume}<br><br>
                    </div>""",
                unsafe_allow_html=True
            )

            # ➡️ Ajouter le titre et le résumé à nos listes
            tous_les_titres.append(titre)
            tous_les_resumes.append(resume)

        # 🧠 ➡️ Après avoir parcouru tous les articles :

        if tous_les_titres and tous_les_resumes:
            st.subheader("=== Synthèse générale ===")

            # 🔹 Concaténer tous les titres pour générer UN titre général
            titres_concatenes = "\n".join(tous_les_titres)
            titre_general = ""
            for chunk in chain_titre_general.stream({"context": titres_concatenes, "language": "francais"}):
                if chunk:
                    titre_general += chunk

            # 🔹 Concaténer tous les résumés pour générer UN résumé général
            resumes_concatenes = "\n".join(tous_les_resumes)
            resume_general_final = ""
            for chunk in chain_resumer_general.stream({"context": resumes_concatenes, "language": "francais"}):
                if chunk:
                    resume_general_final += chunk

            # ➡️ Afficher le titre général et le résumé général final
            st.markdown(
                f"""<div style="text-align: justify;">
                        <h2>Titre Général :</h2>
                        <p><strong>{titre_general}</strong></p><br>
                        <h2 >Résumé Général :</h2>
                        <p><strong>{resume_general_final}</strong></p><br>
                    </div>""",
                unsafe_allow_html=True
            )

    else:
        st.warning("😕 Aucun chunk pertinent trouvé.")
